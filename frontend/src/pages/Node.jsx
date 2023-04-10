import React, { useState, useEffect } from "react";

function EditableEntries() {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetch("https://api.example.com/data")
      .then((response) => response.json())
      .then((data) => {
        setData(data);
        setIsLoading(false);
      })
      .catch((error) => {
        setError(error);
        setIsLoading(false);
      });
  }, []);

  const handleSave = () => {
    setIsSaving(true);
    fetch("https://api.example.com/data", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(() => {
        setIsSaving(false);
      })
      .catch((error) => {
        setError(error);
        setIsSaving(false);
      });
  };

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return <p>Oops! Something went wrong: {error.message}</p>;
  }

  return (
    <div>
      {data.map((entry) => (
        <div key={entry.id}>
          <h2>{entry.title}</h2>
          <label>
            Text Entry:
            <input
              type="text"
              value={entry.text}
              onChange={(e) => {
                const newData = [...data];
                newData[
                  newData.findIndex((item) => item.id === entry.id)
                ].text = e.target.value;
                setData(newData);
              }}
            />
          </label>
          <br />
          <label>
            Checkbox:
            <input
              type="checkbox"
              checked={entry.checked}
              onChange={(e) => {
                const newData = [...data];
                newData[
                  newData.findIndex((item) => item.id === entry.id)
                ].checked = e.target.checked;
                setData(newData);
              }}
            />
          </label>
          <hr />
        </div>
      ))}
      <button onClick={handleSave} disabled={isSaving}>
        {isSaving ? "Saving..." : "Save"}
      </button>
    </div>
  );
}

export default EditableEntries;