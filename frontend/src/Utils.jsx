export const capitalizeId = (inputString) => {
    inputString = inputString.replace(/_/g, ' ');
    return inputString.replace(/\b\w/g, match => match.toUpperCase());
};

// Helper function to render input based on data type
export const getFieldInput = (fieldName, fieldValue, handleInputChange, json) => {
    if (fieldName.endsWith('_options') && Array.isArray(fieldValue)) {
      // Skip rendering for fields ending with "_options"
      return null;
    }
    // Search for matching "_options" fields in the JSON
    const matchingOptionsField = json.find(
      ([optionsFieldName, optionsFieldValue]) => (
        optionsFieldName.endsWith('_options') &&
        optionsFieldValue.length > 0 &&
        optionsFieldName.replace(/_options$/, '') === `${fieldName}`
      )
    );
  
    if (matchingOptionsField) {
      const baseFieldName = fieldName;
      return (
        <select
          className="dropdown"
          id={baseFieldName}
          name={baseFieldName}
          value={json[baseFieldName]}
          onChange={(e) => handleInputChange(baseFieldName, e.target.value)}
        >
          {matchingOptionsField[1].map((option, index) => (
            <option key={index} value={option}>
              {option}
            </option>
          ))}
        </select>
      );
    }
    if (typeof fieldValue === 'boolean') {
      // Render a checkbox for boolean values
      return (
        <input
          type="checkbox"
          id={fieldName}
          name={fieldName}
          checked={fieldValue}
          onChange={(e) => handleInputChange(fieldName, e.target.checked)}
        />
      );
    } else if (typeof fieldValue === 'number') {
      // Render a number input for numeric values
      return (
        <input
          type="number"
          id={fieldName}
          name={fieldName}
          value={fieldValue}
          onChange={(e) => handleInputChange(fieldName, parseFloat(e.target.value))}
        />
      );
    } else {
      // Render a text input for other data types
      return (
        <input
          type="text"
          id={fieldName}
          name={fieldName}
          value={fieldValue || ''}
          onChange={(e) => handleInputChange(fieldName, e.target.value)}
        />
      );
    }
  };