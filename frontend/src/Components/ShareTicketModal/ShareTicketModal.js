import React, {useState, useEffect, useContext, useRef} from 'react';
import {AppContext} from "../../Context/AppContext";
import {Button, Dropdown, Header, Icon, Modal} from "semantic-ui-react";

function ShareTicketModal({handleClose, ticketid, name}) {
    const [appState,] = useContext(AppContext);
    const [users, setUsers] = useState([]);
    const [shareButtonEnabled, setShareButtonEnabled] = useState(false);

    const selectedUserId = useRef("");

    const shareTicket = () => {
        if (selectedUserId.current) {
            appState.api.shareTicket(ticketid, selectedUserId.current).finally(() => {
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
        if (selectedUserId.current){
            setShareButtonEnabled(true);
        }
        else
        {
            setShareButtonEnabled(false);
        }
    };

    return (
        <Modal
            open={true}
            onClose={handleClose}
            basic
            size='small'
            centered={false}
            closeOnDimmerClick={false}
        >
            <Header icon='browser' content='Share access to ticket'/>
            <Modal.Content>
                <h3>This will give selected user access to your session to {name}</h3>
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
                />

            </Modal.Content>
            <Modal.Actions>
                <Button color='green' onClick={shareTicket} disabled={!shareButtonEnabled}>
                    <Icon name='checkmark'/> Share
                </Button>
                <Button color='red' onClick={handleClose}>
                    <Icon name='delete'/> Cancel
                </Button>
            </Modal.Actions>
        </Modal>
    );
}

export default ShareTicketModal;