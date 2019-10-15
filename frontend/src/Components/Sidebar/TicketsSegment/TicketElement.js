import React, {useContext} from "react";
import {AppContext} from "../../../Context/AppContext";
import {Icon, List} from "semantic-ui-react";
import TimeAgo from "react-timeago";


const TicketElement = ({
                           ticket,
                           activatable = true,
                           activateTicket,
                           controlSize = true,
                           activeIndex = 0,
                           setActiveIndex
                       }) => {
    const [appState,] = useContext(AppContext);

    const hideTicketInfo = () => {
        window.removeEventListener("click", hideTicketInfo);
        setActiveIndex(0);
    };

    /***
     * Show/hide clicked ticket info and add listener which will hide info if clicked anywhere else
     * @param e
     */
    const toggleTicketInfo = (e) => {
        e.stopPropagation();
        const id = e.target.getAttribute("index");
        window.removeEventListener("click", hideTicketInfo);
        if (activeIndex !== id) {
            setActiveIndex(id);
            setTimeout(() => {
                window.addEventListener("click", hideTicketInfo);
            }, 10)
        } else {
            setActiveIndex(0);
        }
    };

    const handleTicketClick = (e) => {
        e.stopPropagation();
        activatable && activateTicket(ticket.id, ticket.connection.name, controlSize);
    };

    const formatDateString = (source) => {
        let date = new Date(source);
        return date.getFullYear() + "-" +
            (date.getMonth() + 1).toString().padStart(2, '0') +
            "-" +
            date.getDate().toString().padStart(2, '0') +
            " " +
            date.getHours().toString().padStart(2, '0') + ":" +
            date.getMinutes().toString().padStart(2, '0');
        // + ":" +
        // date.getSeconds().toString().padStart(2, '0')
    };

    return (
        <div index={ticket.id} onClick={toggleTicketInfo} className="ticketItem">

                <span className={activatable ? 'activatable' : ''} onClick={handleTicketClick}>
                    {ticket.connection.name}&nbsp;
                    {ticket.author.id !== appState.user.id && "(" + ticket.author.username + ")"}
                    {ticket.user.id !== appState.user.id && "(" + ticket.user.username + ")"}
                </span>

            <Icon link color='red' inverted name='delete'
                  onClick={() => appState.actions.deleteTicket(ticket.id)}
                  style={{float: "right"}}
            />

            <div className="ticketDetails"
                 style={{
                     display: activeIndex === ticket.id ? "block" : "none",
                 }}>
                <List size="tiny">
                    <List.Item icon='tv' content={<span>{ticket.connection.protocol.toUpperCase()}, ID: <span
                        title={ticket.id}>...{ticket.id.slice(ticket.id.length - 5)}</span> {ticket.parent && <>,
                        Parent ID: {ticket.parent}</>}</span>}/>
                    <List.Item icon='play circle' content={<><TimeAgo title={formatDateString(ticket.created)}
                                                                      date={ticket.created}/></>}/>
                    <List.Item icon='stop circle' content={<><TimeAgo title={formatDateString(ticket.validto)}
                                                                      date={ticket.validto}/></>}/>
                    <List.Item icon='time' content={<span title="Period (days)">{ticket.validityperiod}</span>}/>
                </List>
            </div>
        </div>
    )
};

export default TicketElement;