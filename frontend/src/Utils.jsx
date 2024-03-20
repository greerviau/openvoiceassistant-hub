export const capitalizeId = (inputString) => {
    inputString = inputString.replace(/_/g, ' ');
    return inputString.replace(/\b\w/g, match => match.toUpperCase());
};

// Helper function to render input based on data type
export const getFieldInput = (fieldName, fieldValue, handleInputChange, json) => {
  const handleAddItem = (value) => {
    const newValue = [...fieldValue, value]; // Add the new item to the array
    handleInputChange(fieldName, newValue); // Update the field value
  };

  const handleEditItem = (index, value) => {
    const newValue = [...fieldValue]; // Copy the array
    newValue[index] = value; // Update the value at the specified index
    handleInputChange(fieldName, newValue); // Update the field value
  };

  const handleRemoveItem = (index) => {
    const newValue = [...fieldValue.slice(0, index), ...fieldValue.slice(index + 1)]; // Remove the item at the specified index
    handleInputChange(fieldName, newValue); // Update the field value
  };

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
    return (
      <select
        className="dropdown"
        id={fieldName}
        name={fieldName}
        value={fieldValue}
        onChange={(e) => handleInputChange(fieldName, e.target.value)}
      >
        {matchingOptionsField[1].map((option, index) => (
          <option key={index} value={option}>
            {capitalizeId(option)}
          </option>
        ))}
      </select>
    );
  }

  if (Array.isArray(fieldValue)) {
    return (
      <div>
        {fieldValue.map((item, index) => (
          <div style={{ paddingTop: "10px"}} key={index}>
            <input
              type="text"
              value={item}
              onChange={(e) => handleEditItem(index, e.target.value.trim())}
            />
            <button className="delete-button" onClick={() => handleRemoveItem(index)}>
            <i className="fas fa-trash-alt"></i>
            </button> {/* Call internal handler */}
          </div>
        ))}
        <div style={{ paddingTop: "10px"}}>
          <input
            id={`add_${fieldName}`}
            type="text"
            placeholder="Add new item"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.target.value.trim() !== '') {
                e.preventDefault();
                handleAddItem(e.target.value.trim()); // Add the value to the array when Enter key is pressed
                e.target.value = ''; // Clear the input field
              }
            }}
          />
          <button  className="submit-button" onClick={(e) => {
            e.preventDefault();
            const inputField = document.querySelector(`#add_${fieldName}`);
            if (inputField.value.trim() !== '') {
              handleAddItem(inputField.value.trim()); // Add the value to the array when the button is clicked
              inputField.value = ''; // Clear the input field
            }
          }}>Add</button> {/* Call internal handler */}
        </div>
      </div>
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
