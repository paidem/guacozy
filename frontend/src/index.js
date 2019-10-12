import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './Components/App/App';
import {AppProvider} from "./Context/AppContext";

ReactDOM.render(
    <AppProvider>
        <App/>
    </AppProvider>
    , document.getElementById('root'));