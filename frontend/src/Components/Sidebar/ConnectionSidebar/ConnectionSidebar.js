import React, {useCallback, useContext, useRef, useState} from 'react';
import {Button, Container, Icon, Input, Segment} from "semantic-ui-react";
import './ConnectionSidebar.css'
import ConnectionsTree from "../ConnectionsTree/ConnectionsTree";
import TicketsSegment from "../TicketsSegment/TicketsSegment";
import {AppContext} from "../../../Context/AppContext";
import {LayoutContext} from "../../../Layout/LayoutContext";
import {contextMenu, Item, Menu, Separator, Submenu} from "react-contexify";
import ShareTicketModal from "../../ShareTicketModal/ShareTicketModal";
import {SCREEN_SIZES} from "../../../settings"

function ConnectionSidebar(props) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);
    const [treeNodeFilterString, setTreeNodeFilterString] = useState("");
    const [treeDraggable, setTreeDragable] = useState(false);
    const searchInputRef = useRef();

    const [shareModalProps, setShareModalProps] = useState({
        ticketid: null,
        name: null
    });

    const [shareModalOpen, setShareModalOpen] = useState(false);


    // Use ticket id activate ticket in new tab
    // or find existing tab and focus it
    const activateTicket = useCallback((ticketid, tabName) => {

        let tabTitle = <span
            onContextMenu={(e) => {
                handleTabContextMenuEvent(e, {tabid: ticketid, name: tabName})
            }}>
        {tabName}
        </span>;

        // Activate ticket (this will focus on existing tab or create new tab)
        layoutState.actions.activateTicket(ticketid, tabTitle, true);
    }, [layoutState.actions]);

    // Use connection id to generate/retrieve ticket  and activate ticket in new tab
    // or find existing tab and focus it
    const activateConnection = useCallback((connectionid, tabName) => {
        appState.actions.createTicket(connectionid, appState.user.id,
            (ticketid) => {
                // Activate ticket (this will focus on existing tab or create new tab)
                activateTicket(ticketid, tabName);
                // Update tickets list
                appState.actions.updateTickets();
            })
    }, [appState.actions, appState.user, activateTicket]);

    const duplicateTicket = (originalTicketid, tabName) => {
        appState.actions.duplicateticket(originalTicketid, (ticketid) => {
            activateTicket(ticketid, tabName)
            // update tickets, so ticket list is renewed
            appState.actions.updateTickets();
        })
    };

    const updateScreenSize = (tabid, screenSize) => {
        layoutState.actions.updateTabScreenSize(tabid, screenSize);
    };

    //*************************//
    // Connection context menu //
    //*************************//

    // Context menu to be shown when user clicks on connection
    const ConnectionContextMenu = (props) => {
        return (
            <Menu animation="fade" id="connection_context_menu" theme="dark">
                <Item
                    onClick={({event, props}) => onConnectionContextMenuAction(event, props, "connect")}>Connect</Item>
                <Item
                    onClick={({event, props}) => onConnectionContextMenuAction(event, props, "edit")}>Edit</Item>
                <Separator/>
            </Menu>
        );
    };

    // Connection context menu //
    // Executes when user selects action in tab's name context menu
    const onConnectionContextMenuAction = (event, props, action) => {
        switch (action) {
            case "connect":
                activateConnection(props.id, props.text);
                break;
            default:
                window.alert("Action not implemented: " + action);
        }
    };

    // Connection context menu //
    // Action so handle connection's context menu action
    // Activates menu with "connection_context_menu" (ConnectionContextMenu)
    const handleConnectionContextMenuEvent = (e, data) => {
        e.preventDefault();
        contextMenu.show({
            id: "connection_context_menu",
            event: e,
            props: data
        });
    };

    // *************************** end of Connection context menu ********************************** //


    //******************//
    // Tab context menu //
    //******************//

    const isTicketShared = ({event, props}) => {
        let tickets = appState.tickets.filter(t => t.id === props.tabid && !t.parent);
        return tickets.length === 0;
    };

    // Context menu to be shown when user clicks on tab's name
    const TabContextMenu = (props) => {
        return (
            <Menu animation="fade" id="tab_context_menu" theme="dark">
                <Item
                    onClick={({event, props}) => onTabContextMenuAction(event, props, "reconnect")}>Reconnect</Item>
                <Separator/>
                <Item disabled={isTicketShared}
                      onClick={({event, props}) => onTabContextMenuAction(event, props, "share")}>Share</Item>
                <Separator/>
                <Item disabled={isTicketShared}
                      onClick={({event, props}) => onTabContextMenuAction(event, props, "duplicate")}>Duplicate</Item>
                <Separator/>
                <Item
                    onClick={({event, props}) => onTabContextMenuAction(event, props, "disconnect")}>Close</Item>
                <Submenu label="Screen size">
                    <Item onClick={({event, props}) => onTabContextMenuAction(event, {
                        ...props,
                        screenSize: null
                    }, "screenSize")}>Auto</Item>
                    {SCREEN_SIZES.map(size =>
                        <Item onClick={({event, props}) => onTabContextMenuAction(event, {
                            ...props,
                            screenSize: {width: size[0], height: size[1]}
                        }, "screenSize")}>{size[0]} x {size[1]}</Item>
                    )
                    }
                </Submenu>
            </Menu>
        );
    };

    // Executes when user selects action in tab's name context menu
    const onTabContextMenuAction = (event, props, action) => {
        // When menu is clicked, it is over other element and we need to stop
        // propagation, otherwise it conflicts with other events
        event.stopPropagation();

        switch (action) {
            case "reconnect":
                layoutState.actions.refreshTab(props.tabid);
                break;
            case "share":
                setShareModalProps({
                    ticketid: props.tabid,
                    name: props.name
                });
                setShareModalOpen(true);
                break;
            case "disconnect":
                layoutState.actions.deleteTab(props.tabid);
                break;
            case "duplicate":
                duplicateTicket(props.tabid, props.name);
                break;
            case "screenSize":
                updateScreenSize(props.tabid, props.screenSize);
                break;
            default:
                window.alert("Wrong action: " + action)
        }
    };

    // Action so handle tab's name context menu action
    // Activates menu with "tab_context_menu" (TabContextMenu)
    const handleTabContextMenuEvent = (e, data) => {
        e.preventDefault();
        contextMenu.show({
            id: "tab_context_menu",
            event: e,
            props: data
        });
    };

    // ************************ end of Tab context menu ****************************** //


    /***
     * Takes node and returns it's representation. By default representation is just text
     * but here we use it mainly to bind to onDoubleClick event when clicking on connection node
     * @param node
     * @returns {*}
     */
    const nodeTitleConstructor = (node) => {
        if (node.isFolder) {
            return <span>{node.text}</span>
        } else {
            return <span
                onDoubleClick={() => activateConnection(node.id, node.text)}
                onContextMenu={(e) => {
                    handleConnectionContextMenuEvent(e, {
                        id: node.id.toString(),
                        text: node.text
                    })
                }}
            >{node.text}</span>
        }
    };

    const handleShareModalClose = () => {
        setShareModalProps({ticketid: null, name: null});
        setShareModalOpen(false);
        appState.actions.updateTickets();
    };

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
                        className='topButton'
                        loading={appState.connectionsLoading || appState.ticketsLoading}
                        onClick={() => {
                            appState.actions.updateConnections();
                            appState.actions.updateTickets();
                        }
                        }
                />
                <Button icon='bars'
                        color={treeDraggable ? 'green' : 'grey'}
                        basic
                        size='mini'
                        title='Rearrange'
                        className='topButton'
                        onClick={() => setTreeDragable(!treeDraggable)}
                />
                <ConnectionsTree searchString={treeNodeFilterString}
                                 draggable={treeDraggable}
                                 nodeTitleConstructor={nodeTitleConstructor}
                                 disableDraggebleMode={() => {
                                     setTreeDragable(false)
                                 }}
                />
            </Segment>
            <Segment raised color='grey' className='ticketList'>
                <TicketsSegment
                    searchString={treeNodeFilterString}
                    activateTicket={activateTicket}
                />
            </Segment>
            <ConnectionContextMenu/>
            <TabContextMenu/>
            {shareModalOpen && <ShareTicketModal {...shareModalProps}
                                                 handleClose={handleShareModalClose}/>}
        </Container>
    );
}

export default ConnectionSidebar;