import React, {useContext, useState} from 'react';
import GuacozyApi from "../Api/GuacozyApi";
import {LayoutContext} from "../Layout/LayoutContext";
import {handleTabContextMenuEvent} from "../Components/ContextMenu/TabContextMenu";

const api = new GuacozyApi();

const AppContext = React.createContext([{}, () => {
}]);

const AppProvider = (props) => {
    const [layoutState,] = useContext(LayoutContext);

    const checkLoginStatus = (retriesLeft) => {
        retriesLeft--;

        api.getCurrentUser()
            .then(r => {
                setState(oldState => ({...oldState, apiError: null, user: r.data}));
                updateConnections();
                updateTickets();
            })
            .catch(e => {
                    if (!e.response) {
                        setState(oldState => ({
                            ...oldState,
                            apiError: "No response. Retries left: " + retriesLeft,
                            user: null
                        }));
                        if (retriesLeft > 0) {
                            setTimeout(() => checkLoginStatus(retriesLeft), 2000);
                        }
                    } else {
                        setState(oldState => ({...oldState, apiError: null, user: null}));
                        window.location.href = "/accounts/login/";
                    }
                }
            )
    };

    const logout = () => {
        api.logout().then(() => {
                // setState(defaultState);
                window.location.href = "/accounts/login/";
            }
        )
    };

    const updateConnections = () => {
        setState((state) => ({...state, connectionsLoading: true}));
        api.getConnections()
            .then(r => {
                    setState(state => ({...state, connections: r.data}))
                }
            )
            .finally(() => {
                setState((state) => ({...state, connectionsLoading: false}));
            })
    };

    const updateTickets = () => {
        setState((state) => ({...state, ticketsLoading: true}));

        api.getTickets()
            .then(r => {
                let newTickets = r.data;
                newTickets.sort((a, b) => (a.connection.name > b.connection.name) ? 1 : (a.connection.name < b.connection.name ? -1 : 0));
                newTickets = newTickets.map(ticket => ({
                    ...ticket,
                    created: Date.parse(ticket.created),
                    validto: Date.parse(ticket.validto),
                }));
                setState(state => ({...state, tickets: newTickets}));
            })
            .finally(() => {
                setState((state) => ({...state, ticketsLoading: false}));
            })
    };

    /*
    * Crete new access ticket given Connection and User
    * most of the time user is the same as app user
    * but it may be different when feature to provide other 
    * access to connection is added
     */
    const createTicket = (connectionUUID, userid, callback) => {
        api.createTicket(connectionUUID, userid, callback);
    };

    /*
    * Duplicate existing ticket
     */
    const duplicateticket = (ticketid, callback) => {
        api.duplicateTicket(ticketid, callback);
    };

    const deleteTicket = (ticketid) => {
        // delete ticket from state before makeing API call - optimistic delete
        setState(state => ({...state, tickets: state.tickets.filter(ticket => ticket.id !== ticketid)}));

        api.deleteTicket(ticketid)
            .finally(() => {
                // if we have a tab with this ticket - it should also be deleted
                layoutState.actions.deleteTab(ticketid);
                updateTickets();
            })
    };

    // Use ticket id activate ticket in new tab
    // or find existing tab and focus it
    const activateTicket = (ticketid, tabName, controlSize = true, controlInput = true) => {

        let tabTitle = <span
            onContextMenu={(e) => {
                handleTabContextMenuEvent(e, {tabid: ticketid, name: tabName})
            }}>
        {tabName}
        </span>;

        // Activate ticket (this will focus on existing tab or create new tab)
        layoutState.actions.activateTicket(ticketid, tabTitle, controlSize, controlInput);
    };

    // Use connection id to generate/retrieve ticket  and activate ticket in new tab
    // or find existing tab and focus it
    const activateConnection = (connectionid, tabName, user) => {
        createTicket(connectionid, user.id,
            (ticketid) => {
                // Activate ticket (this will focus on existing tab or create new tab)
                activateTicket(ticketid, tabName);
                // Update tickets list
                updateTickets();
            })
    };

    const openModal = ({type, data}) => {
        let modal = React.createElement(type, props = {
                data: data,
                handleClose: () => {
                    setState(state => ({...state, activeModal: null}));
                }
            }
        );

        setState(state => ({...state, activeModal: modal}));
    };

    const defaultState = {
        api: api,
        apiError: null,
        activeModal: null,
        connections: [],
        connectionsLoading: false,
        tickets: [],
        ticketsLoading: false,
        confirmedUnsafeConnection: false,
        user: null,
        actions: {
            activateConnection: activateConnection,
            activateTicket: activateTicket,
            checkLoginStatus: checkLoginStatus,
            createTicket: createTicket,
            deleteTicket: deleteTicket,
            duplicateticket: duplicateticket,
            openModal: openModal,
            logout: logout,
            updateConnections: updateConnections,
            updateTickets: updateTickets,
        }
    };

    const [state, setState] = useState(defaultState);

    return (
        <AppContext.Provider value={[state, setState]}>
            {props.children}
        </AppContext.Provider>
    );
};

export {AppContext, AppProvider};