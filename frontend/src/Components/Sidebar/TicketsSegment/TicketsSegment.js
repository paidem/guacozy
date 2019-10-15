import React, {useContext, useState} from 'react';
import {Accordion, Icon} from "semantic-ui-react";
import TicketsList from "./TicketsList";
import {AppContext} from "../../../Context/AppContext";
import {LayoutContext} from "../../../Layout/LayoutContext";

function TicketsSegment({searchString}) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);

    const [ticketListVisible, setTicketListVisible] = useState(true);

    const activateTicket = (ticketUUID, tabName, controlSize, tabTitleConstructor) => {
        // create tab with this ticket's connection
        // and attach context menu handler to it
        layoutState.actions.activateTicket(ticketUUID, tabTitleConstructor(ticketUUID, tabName), controlSize);
    };

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
                             activateTicket={activateTicket}
                             searchString={searchString}
                />
            </Accordion.Content>
        </Accordion>
    );
}

export default TicketsSegment;