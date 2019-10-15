import React, {useContext, useState} from 'react';
import {Accordion, Icon} from "semantic-ui-react";
import TicketsList from "./TicketsList";
import {AppContext} from "../../../Context/AppContext";

function TicketsSegment({searchString, activateTicket}) {
    const [appState,] = useContext(AppContext);

    const [ticketListVisible, setTicketListVisible] = useState(true);

    return (
        <Accordion>
            <Accordion.Title
                active={ticketListVisible}
                onClick={() => {
                    setTicketListVisible(!ticketListVisible)
                }}>
                <Icon name='dropdown'/>
                Active tickets
            </Accordion.Title>
            <Accordion.Content active={ticketListVisible}>
                <TicketsList tickets={appState.tickets}
                             searchString={searchString}
                />
            </Accordion.Content>
        </Accordion>
    );
}

export default TicketsSegment;