import React, { useState, useEffect } from 'react';
import useOpenController from "../useOpenController";
import JSONInput from 'react-json-editor-ajrm';
import locale    from 'react-json-editor-ajrm/locale/en';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronDown } from '@fortawesome/free-solid-svg-icons';

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
      {isOpen && <TextSection component={label} data={data?.config} />}
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
        <FontAwesomeIcon icon={faChevronDown} />
      </button>
    </div>
  );
};

export const TextSection = ({ component, data }) => {

  const [newData, setNewData] = useState(JSON.stringify(data, null, 2));

  function handleChange(d, event) {
    try {
      setNewData(d.json);
    } catch (error) {
      // pass, user is editing
    }
  }

  const handleUpdate = (e) => {
    console.log(newData)
    fetch(`/components/${component}/config`, {
              method: 'PUT',
              headers: new Headers({
                 'Accept': 'application/json',
                 'Content-Type': 'application/json'
              }),
              body: newData
          })
  }

  return (
    <div className="text-container">
      <JSONInput
        id          = {component}
        placeholder = { data }
        locale      = { locale }
        onChange    = {handleChange}
        height      = '100px'
      />
      <button onClick={handleUpdate}>Save</button>
    </div>
  );
};