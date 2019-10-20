import React, {useContext, useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AppContext} from "../../Context/AppContext";
import {Button, Dropdown, Header, Icon, Modal} from "semantic-ui-react";
import ModalBase from "./ModalBase";

function ShareTicketModal({handleClose, data}) {
    const [appState,] = useContext(AppContext);
    const [users, setUsers] = useState([]);
    const [shareButtonEnabled, setShareButtonEnabled] = useState(false);
    const [ticket, setTicket] = useState(null);

    const ticketid = data.id;

    useLayoutEffect(() => {
        let tickets = appState.tickets.filter(t => t.id === ticketid);
        setTicket(tickets.length > 0 ? tickets[0] : null);
    }, [ticketid, appState.tickets]);

    const selectedUserId = useRef("");

    const shareTicket = () => {
        if (selectedUserId.current) {
            appState.api.shareTicket(ticketid, selectedUserId.current).finally(() => {
                appState.actions.updateTickets();
                handleClose();
            });
        }
    };

    useEffect(() => {
        appState.api.getUsers()
            .then(res => {
                setUsers(res.data)
            })
    }, [appState.api]);

    const userOptions = users
        .filter(user => user.id !== appState.user.id) // filter out current user
        .map(user => ({
            key: "user-" + user.id,
            value: user.id,
            text: user.full_name + " (" + user.username + ")"
        }));

    const onUserSelected = (e, data) => {
        selectedUserId.current = data.value;
        updateShareButtonStatus();
    };

    const updateShareButtonStatus = () => {
        if (selectedUserId.current) {
            setShareButtonEnabled(true);
        } else {
            setShareButtonEnabled(false);
        }
    };

    return (
        <ModalBase handleClose={handleClose}>
            <Header icon='browser' content='Share access to ticket'/>
            <Modal.Content>
                {ticket && <>
                    <h3>This will give selected user access to your session ({ticket.connection.name})</h3>
                    User:
                    <Dropdown
                        placeholder='Select user'
                        fluid
                        search
                        selection
                        options={userOptions}
                        floating
                        onChange={onUserSelected}
                        clearable
                    /> </>}
            </Modal.Content>
            <Modal.Actions>
                <Button color='green' onClick={shareTicket} disabled={!shareButtonEnabled}>
                    <Icon name='checkmark'/> Share
                </Button>
                <Button color='gray' onClick={handleClose}>
                    <Icon name='delete'/> Cancel
                </Button>
            </Modal.Actions>
        </ModalBase>
    );
}

export default ShareTicketModal;