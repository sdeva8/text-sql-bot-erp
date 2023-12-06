// store.js
import { createStore } from 'redux';
import chatReducer from './reducer';

const store = createStore(chatReducer);

export default store;
