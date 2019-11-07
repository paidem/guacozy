import React, {useContext, useRef, useState} from 'react';
import {Button, Container, Icon, Input, Segment} from "semantic-ui-react";
import './ConnectionSidebar.css'
import ConnectionsTree from "../ConnectionsTree/ConnectionsTree";
import TicketsSegment from "../TicketsSegment/TicketsSegment";
import {AppContext} from "../../../Context/AppContext";

function ConnectionSidebar(props) {
    const [appState,] = useContext(AppContext);
    const [treeNodeFilterString, setTreeNodeFilterString] = useState("");
    const [treeDraggable, setTreeDragable] = useState(false);
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
                <Button icon='refresh'
                        color='grey'
                        basic inverted
                        size='mini'
                        title='Reload'
                        className='topButtonRight'
                        loading={appState.connectionsLoading || appState.ticketsLoading}
                        onClick={() => {
                            appState.actions.updateConnections();
                            appState.actions.updateTickets();
                        }
                        }
                />
                <Button icon='bars'
                        color={treeDraggable ? 'green' : 'grey'}
                        disabled={treeNodeFilterString !== ""}
                        basic
                        size='mini'
                        title='Rearrange'
                        className='topButtonRight'
                        onClick={() => setTreeDragable(!treeDraggable)}
                />
                <ConnectionsTree searchString={treeNodeFilterString}
                                 draggable={treeDraggable}
                                 disableDraggebleMode={() => {
                                     setTreeDragable(false)
                                 }}
                />
            </Segment>
            <Segment raised color='grey' className='ticketList'>
                <TicketsSegment
                    searchString={treeNodeFilterString}
                />
            </Segment>

        </Container>
    );
}

export default ConnectionSidebar;