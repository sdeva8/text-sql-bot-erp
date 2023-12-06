// actions.js
export const addMessage = (type, message, image = null) => ({
    type: 'ADD_MESSAGE',
    payload: { type, message, image },
  });
  
  export const clearMessages = () => ({
    type: 'CLEAR_MESSAGES',
  });
  
  export const sendMessage = (query) => async (dispatch) => {
    // Add user message to the Redux store
    dispatch(addMessage('user', query, null));
  
    // Simulate a delay before receiving the server response (500ms)
    await new Promise((resolve) => setTimeout(resolve, 500));
  
    try {
      // Modify the server URL to include the 'q' parameter
      const serverUrl = `http://10.0.0.154:8000?${new URLSearchParams({ q: query })}`;
  
      // Fetch data from the modified URL
      const serverMessage = await fetch(serverUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'text/plain',
        },
      }).then((response) => response.text());
  
      // Add server message to the Redux store
      const parsedServerResponse = JSON.parse(serverMessage);
      console.log(parsedServerResponse)
      // Add parsed server message to the Redux store
      // Add parsed server message to the Redux store
      parsedServerResponse.data =  parsedServerResponse.data || [{"data" : "Nothing here"}]
      parsedServerResponse.gen =  parsedServerResponse.gen || [{"LLM" : "Issue"}]
      parsedServerResponse.errors =  parsedServerResponse.errors || [{"errors" : "Error"}]
      dispatch(addMessage('server', parsedServerResponse, null));
  } catch (error) {
    console.error('Error fetching or parsing data:', error);
    // Handle errors if needed
    dispatch(addMessage('server',{data : [{"data" : "issue"}], gen : [{"LLM" : "issue"}], errors : [{"error": toString(error)}]}, null));
  }
      // Handle errors if neede
  };
  
  