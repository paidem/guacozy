import React, {useContext, useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AppContext} from "../../Context/AppContext";
import {Button, Form, Header, Icon, Label, Message, Modal} from "semantic-ui-react";
import ModalBase from "./ModalBase";
import {VALIDITY_PERIOD_OPTIONS} from "../../settings";
import {formatDateString} from "../../Utils/formateDateString";
import TimeAgo from "react-timeago/lib";

function ShareTicketModal({handleClose, data}) {
    const [appState,] = useContext(AppContext);
    const [error, setError] = useState(null);
    const [users, setUsers] = useState([]);
    const [ticket, setTicket] = useState(null);

    const ticketid = data.id;

    // Find ticket object
    useLayoutEffect(() => {
        let tickets = appState.tickets.filter(t => t.id === ticketid);
        setTicket(tickets.length > 0 ? tickets[0] : null);
        console.log(tickets[0])
    }, [ticketid, appState.tickets]);

    // Get latest list of users
    useEffect(() => {
        appState.api.getUsers()
            .then(res => {
                setUsers(res.data)
            })
    }, [appState.api]);

    // Populate user dropdown
    const userOptions = users
        .filter(user => user.id !== appState.user.id) // filter out current user
        .map(user => ({
            key: "user-" + user.id,
            value: user.id,
            text: user.full_name + " (" + user.username + ")"
        }));

    // Form state
    const [formData, setFormData] = useState({userid: null, validityPeriod: VALIDITY_PERIOD_OPTIONS[0].value, control: false});

    // Form handleChange
    const handleChange = (e, {name, value, checked}) => {
        setFormData(state => ({...state, [name]: value ? value : checked}));
    };

    const ticketValidityMessageEl = () => {
        let newTicketValidTo = new Date(ticket.created + formData.validityPeriod*1000);

        let validToMessage = "";

        if (newTicketValidTo > ticket.validto){
            validToMessage += formatDateString(ticket.validto);
            validToMessage += " (capped to your ticket validity)";
        }
        else{
            validToMessage += formatDateString(newTicketValidTo);
        }


        return <React.Fragment>
            <p>Your ticket valid till {formatDateString(ticket.validto)} ({<TimeAgo date={ticket.validto}/>})</p>
            <p>Shared ticket valid till {validToMessage}</p>
        </React.Fragment>
    };

    // Action
    const shareTicket = () => {
        if (formData.userid) {
            appState.api.shareTicket({
                ticketid: ticket.id,
                userid: formData.userid,
                validityPeriod: formData.validityPeriod,
                control: formData.control,
            })
                .then(() => {
                    appState.actions.updateTickets();
                    handleClose();
                })
                .catch((error) => {
                    if (error.response && error.response.data && error.response.data.detail) {
                        setError(error.response.data.detail);
                    } else {
                        // objects are not valid react child and we render error verbatim, so to make it string, concat
                        setError("" + error);
                    }
                });
        }
    };


    return (
        <ModalBase handleClose={handleClose}>
            <Header icon='browser' content='Share access to ticket'/>
            <Modal.Content>
                {ticket && <>
                    <h3>This will give selected user access to your session ({ticket.connection.name})</h3>
                    {error && <Message negative content={error}/>}
                    {ticketValidityMessageEl()}
                    <Form inverted onSubmit={(e) => {
                        e.preventDefault();
                    }}>
                        <Form.Dropdown
                            name="userid"
                            button
                            placeholder='Select user'
                            fluid
                            search
                            selection
                            options={userOptions}
                            // floating
                            onChange={handleChange}
                            clearable
                            value={formData.userid}
                        />
                        <Form.Group widths='equal'>
                            <Form.Dropdown name="validityPeriod"
                                           label="Validity period"
                                           options={VALIDITY_PERIOD_OPTIONS}
                                           onChange={handleChange}
                                           value={formData.validityPeriod}
                            />
                            <Form.Checkbox
                                name="control"
                                onChange={handleChange}
                                label={<label>Allow input (keyboard/mouse)</label>}
                                value={formData.allow}
                            />
                        </Form.Group>
                    </Form>

                </>}
            </Modal.Content>
            <Modal.Actions>
                <Button color='green' onClick={shareTicket} disabled={!formData.userid}>
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