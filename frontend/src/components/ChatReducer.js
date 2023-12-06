// reducer.js
const initialState = {
    messages: [],
  };
  
  const chatReducer = (state = initialState, action) => {
    switch (action.type) {
      case 'ADD_MESSAGE':
        return {
          ...state,
          messages: [...state.messages, action.payload],
        };
      case 'CLEAR_MESSAGES':
        return {
          ...state,
          messages: [],
        };
      default:
        return state;
    }
  };
  
  export default chatReducer;
  