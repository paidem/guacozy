import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'flexlayout-react/style/dark.css'
import 'react-contexify/dist/ReactContexify.min.css';
import App from './Components/App/App';
import {AppProvider} from "./Context/AppContext";
import {LayoutProvider} from "./Layout/LayoutContext";

ReactDOM.render(
    <LayoutProvider>
        <AppProvider>
            <App/>
        </AppProvider>
    </LayoutProvider>
    , document.getElementById('root'));