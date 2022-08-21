from spacy.lang.en import English
import spacy

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECTS = ["dobj", "dative", "attr", "oprd"]
ADJECTIVES = ["acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm",
              "hmod", "infmod", "xcomp", "rcmod", "poss"," possessive"]
COMPOUNDS = ["compound"]
PREPOSITIONS = ["prep"]

class NLExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.parser = English()

    def extract_from_command(self, text):
        doc = self.nlp(text)
        print(doc)
        for tok in doc:
            print(tok.pos_)
        self.extract_subject_object(doc)
        #print(svaos)

    def extract_subject_object(self, doc):
        for token in doc:
            # extract subject
            if (token.dep_=='nsubj'):
                print(token.text)
            # extract object
            elif (token.dep_=='dobj'):
                print(token.text)
                
    def getSubsFromConjunctions(self, subs):
        moreSubs = []
        for sub in subs:
            # rights is a generator
            rights = list(sub.rights)
            rightDeps = {tok.lower_ for tok in rights}
            if "and" in rightDeps:
                moreSubs.extend([tok for tok in rights if tok.dep_ in SUBJECTS or tok.pos_ == "NOUN"])
                if len(moreSubs) > 0:
                    moreSubs.extend(self.getSubsFromConjunctions(moreSubs))
        return moreSubs

    def getObjsFromConjunctions(self, objs):
        moreObjs = []
        for obj in objs:
            # rights is a generator
            rights = list(obj.rights)
            rightDeps = {tok.lower_ for tok in rights}
            if "and" in rightDeps:
                moreObjs.extend([tok for tok in rights if tok.dep_ in OBJECTS or tok.pos_ == "NOUN"])
                if len(moreObjs) > 0:
                    moreObjs.extend(self.getObjsFromConjunctions(moreObjs))
        return moreObjs

    def getVerbsFromConjunctions(self, verbs):
        moreVerbs = []
        for verb in verbs:
            rightDeps = {tok.lower_ for tok in verb.rights}
            if "and" in rightDeps:
                moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
                if len(moreVerbs) > 0:
                    moreVerbs.extend(self.getVerbsFromConjunctions(moreVerbs))
        return moreVerbs

    def findSubs(self, tok):
        head = tok.head
        while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
            head = head.head
        if head.pos_ == "VERB":
            subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
            if len(subs) > 0:
                verbNegated = self.isNegated(head)
                subs.extend(self.getSubsFromConjunctions(subs))
                return subs, verbNegated
            elif head.head != head:
                return self.findSubs(head)
        elif head.pos_ == "NOUN":
            return [head], self.isNegated(tok)
        return [], False

    def isNegated(self, tok):
        negations = {"no", "not", "n't", "never", "none"}
        for dep in list(tok.lefts) + list(tok.rights):
            if dep.lower_ in negations:
                return True
        return False

    def findSVs(self, tokens):
        svs = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
        for v in verbs:
            subs, verbNegated = self.getAllSubs(v)
            if len(subs) > 0:
                for sub in subs:
                    svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
        return svs

    def getObjsFromPrepositions(self, deps):
        objs = []
        for dep in deps:
            if dep.pos_ == "ADP" and dep.dep_ == "prep":
                objs.extend([tok for tok in dep.rights if tok.dep_  in OBJECTS or (tok.pos_ == "PRON" and tok.lower_ == "me")])
        return objs

    def getAdjectives(self, toks):
        toks_with_adjectives = []
        for tok in toks:
            adjs = [left for left in tok.lefts if left.dep_ in ADJECTIVES]
            adjs.append(tok)
            adjs.extend([right for right in tok.rights if tok.dep_ in ADJECTIVES])
            tok_with_adj = " ".join([adj.lower_ for adj in adjs])
            toks_with_adjectives.extend(adjs)

        return toks_with_adjectives

    def getObjsFromAttrs(self, deps):
        for dep in deps:
            if dep.pos_ == "NOUN" and dep.dep_ == "attr":
                verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
                if len(verbs) > 0:
                    for v in verbs:
                        rights = list(v.rights)
                        objs = [tok for tok in rights if tok.dep_ in OBJECTS]
                        objs.extend(self.getObjsFromPrepositions(rights))
                        if len(objs) > 0:
                            return v, objs
        return None, None

    def getObjFromXComp(self, deps):
        for dep in deps:
            if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
                v = dep
                rights = list(v.rights)
                objs = [tok for tok in rights if tok.dep_ in OBJECTS]
                objs.extend(self.getObjsFromPrepositions(rights))
                if len(objs) > 0:
                    return v, objs
        return None, None

    def getAllSubs(self, v):
        verbNegated = self.isNegated(v)
        subs = [tok for tok in v.lefts if tok.dep_ in SUBJECTS and tok.pos_ != "DET"]
        if len(subs) > 0:
            subs.extend(self.getSubsFromConjunctions(subs))
        else:
            foundSubs, verbNegated = self.findSubs(v)
            subs.extend(foundSubs)
        return subs, verbNegated

    def getAllObjs(self, v):
        # rights is a generator
        rights = list(v.rights)
        objs = [tok for tok in rights if tok.dep_ in OBJECTS]
        objs.extend(self.getObjsFromPrepositions(rights))

        potentialNewVerb, potentialNewObjs = self.getObjFromXComp(rights)
        if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
            objs.extend(potentialNewObjs)
            v = potentialNewVerb
        if len(objs) > 0:
            objs.extend(self.getObjsFromConjunctions(objs))
        return v, objs

    def getAllObjsWithAdjectives(self, v):
        # rights is a generator
        rights = list(v.rights)
        objs = [tok for tok in rights if tok.dep_ in OBJECTS]

        if len(objs)== 0:
            objs = [tok for tok in rights if tok.dep_ in ADJECTIVES]

        objs.extend(self.getObjsFromPrepositions(rights))

        potentialNewVerb, potentialNewObjs = self.getObjFromXComp(rights)
        if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
            objs.extend(potentialNewObjs)
            v = potentialNewVerb
        if len(objs) > 0:
            objs.extend(self.getObjsFromConjunctions(objs))
        return v, objs

    def findSVOs(self, tokens):
        svos = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
        for v in verbs:
            subs, verbNegated = self.getAllSubs(v)
            # hopefully there are subs, if not, don't examine this verb any longer
            if len(subs) > 0:
                v, objs = self.getAllObjs(v)
                for sub in subs:
                    for obj in objs:
                        objNegated = self.isNegated(obj)
                        svos.append((sub.lower_, "!" + v.lower_ if verbNegated or objNegated else v.lower_, obj.lower_))
        return svos

    def findSVAOs(self, doc):
        svos = []
        verbs = [tok for tok in doc if tok.pos_ == "VERB" and tok.dep_ != "aux"]
        for v in verbs:
            subs, verbNegated = self.getAllSubs(v)
            # hopefully there are subs, if not, don't examine this verb any longer
            if len(subs) > 0:
                v, objs = self.getAllObjsWithAdjectives(v)
                for sub in subs:
                    for obj in objs:
                        objNegated = self.isNegated(obj)
                        obj_desc_tokens = self.generate_left_right_adjectives(obj)
                        sub_compound = self.generate_sub_compound(sub)
                        svos.append((" ".join(tok.lower_ for tok in sub_compound), "!" + v.lower_ if verbNegated or objNegated else v.lower_, " ".join(tok.lower_ for tok in obj_desc_tokens)))
        return svos

    def generate_sub_compound(self, sub):
        sub_compunds = []
        for tok in sub.lefts:
            if tok.dep_ in COMPOUNDS:
                sub_compunds.extend(self.generate_sub_compound(tok))
        sub_compunds.append(sub)
        for tok in sub.rights:
            if tok.dep_ in COMPOUNDS:
                sub_compunds.extend(self.generate_sub_compound(tok))
        return sub_compunds

    def generate_left_right_adjectives(self, obj):
        obj_desc_tokens = []
        for tok in obj.lefts:
            if tok.dep_ in ADJECTIVES:
                obj_desc_tokens.extend(self.generate_left_right_adjectives(tok))
        obj_desc_tokens.append(obj)

        for tok in obj.rights:
            if tok.dep_ in ADJECTIVES:
                obj_desc_tokens.extend(self.generate_left_right_adjectives(tok))

        return obj_desc_tokens