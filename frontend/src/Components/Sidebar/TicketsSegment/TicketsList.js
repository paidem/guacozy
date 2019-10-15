import React, {useContext, useState} from 'react';
import {AppContext} from "../../../Context/AppContext";
import {Accordion, SegmentGroup} from "semantic-ui-react";
import TicketElement from "./TicketElement";

function TicketsList({searchString}) {
    const [appState,] = useContext(AppContext);
    const [activeIndex, setActiveIndex] = useState(0);

    const list = searchString ?
        appState.tickets.filter(ticket =>
            ticket.connection.name
            .toLowerCase()
            .includes(searchString.toLowerCase()))
        : appState.tickets;

    const myTickets = list.filter(t => t.author.id === appState.user.id && t.user.id === appState.user.id);
    const sharedWithMe = list.filter(t => t.author.id !== t.user.id && t.author.id !== appState.user.id);
    const sharedByMe = list.filter(t => t.author.id !== t.user.id && t.author.id === appState.user.id);

    return (
        <React.Fragment>
            {list.length > 0 ?
                <SegmentGroup className='ticketList'>
                    <Accordion>
                        {myTickets.length > 0 &&
                        <div className="ticketSection">
                            <span className="ticketSectionHeader">My tickets</span>
                            {myTickets.map(ticket =>
                                <TicketElement key={ticket.id}
                                               ticket={ticket}
                                               activeIndex={activeIndex}
                                               setActiveIndex={setActiveIndex}/>)}
                        </div>}

                        {sharedWithMe.length > 0 &&
                        <div className="ticketSection">
                            <span className="ticketSectionHeader">Shared with me:</span>
                            {sharedWithMe.map(ticket =>
                                <TicketElement key={ticket.id}
                                               ticket={ticket}
                                               controlSize={false}
                                               activeIndex={activeIndex}
                                               setActiveIndex={setActiveIndex}/>)}
                        </div>}

                        {sharedByMe.length > 0 &&
                        <div className="ticketSection">
                            <span className="ticketSectionHeader">Shared by me:</span>
                            {sharedByMe.map(ticket =>
                                <TicketElement key={ticket.id}
                                               ticket={ticket}
                                               activatable={false}
                                               activeIndex={activeIndex}
                                               setActiveIndex={setActiveIndex}/>)}
                        </div>}
                    </Accordion>
                </SegmentGroup>
                :
                <div style={{width: "100%", textAlign: "center"}}>
                    {appState.tickets.length > 0 ? "no results" : "no active tickets"}
                </div>
            }
        </React.Fragment>
    );
}

export default TicketsList;