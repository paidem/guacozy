import React, {useRef, useState} from 'react';
import {Container, Icon, Input, Segment} from "semantic-ui-react";
import './ConnectionSidebar.css'
import ConnectionsTree from "../ConnectionsTree/ConnectionsTree";

function ConnectionSidebar(props) {
    const [treeNodeFilterString, setTreeNodeFilterString] = useState("");
    const searchInputRef = useRef();

    return (
        <Container className='sidebarContainer'>
            <Segment className='searchInputSegment' raised color='blue'>
                <Input size='small' fluid icon placeholder='Search...'
                       value={treeNodeFilterString}
                       onChange={(event) => {
                           setTreeNodeFilterString(event.target.value)
                       }}
                       onKeyDown={(event) => {
                           // Handle Esc button to clear
                           let code = event.charCode || event.keyCode;
                           code === 27 && setTreeNodeFilterString("")
                       }}
                       ref={searchInputRef}>
                    <input/>
                    <Icon name='times circle outline' size='large' link
                          onClick={() => setTreeNodeFilterString("")}/>
                </Input>
            </Segment>
            <Segment raised color='grey' className='connectionList'>
                <ConnectionsTree searchString={treeNodeFilterString} draggable={false}/>
            </Segment>
        </Container>
    );
}

export default ConnectionSidebar;