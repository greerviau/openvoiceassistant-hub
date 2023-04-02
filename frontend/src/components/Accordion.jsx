import React from "react";
import useOpenController from "../useOpenController";

export const Accordion = ({ label, data }) => {
  const { isOpen, toggle } = useOpenController(false);
  return (
    <div className="accordion-container">
      <ExpendableColumn
        title={label}
        options={data?.algorithm_options}
        isOpen={isOpen}
        toggle={toggle}
      />
      {isOpen && <TextSection data={data?.config} />}
      <div className="underline"></div>
    </div>
  );
};

export const ExpendableColumn = ({ title, options, isOpen, toggle }) => {

  const MakeItem = function(X) {
    return <option>{X}</option>;
  };
  
  return (
    <div className="column-container" onClick={toggle}>
      <div className="column-text">{title}</div>
      {
        options && <select>{options.map(MakeItem)}</select>
      }
      <button className="expendable-button">
        <span
          class="material-symbols-outlined"
          style={{
            transform: `rotate(${isOpen ? 180 : 0}deg)`,
            transition: "all 0.25s",
          }}
        >
          expand_more
        </span>
      </button>
    </div>
  );
};

export const TextSection = ({ data }) => {
  return (
    <div className="text-container">
    </div>
  );
};