import React, {useContext,} from 'react';
import {Container} from "semantic-ui-react";
import {AppContext} from "../../../Context/AppContext";
import './ConnectionSidebar.css'

function ConnectionSidebar(props) {
    const [appState,] = useContext(AppContext);

    return (
        <Container className='sidebarContainer'>
            Sidebar
        </Container>
    );
}

export default ConnectionSidebar;