import React, {useContext} from 'react';
import {Button, Divider, Icon, Label, Segment, Statistic} from "semantic-ui-react";
import {AppContext} from "../../Context/AppContext";
import Container from "semantic-ui-react/dist/commonjs/elements/Container";


function Welcome(props) {
    const [appState,] = useContext(AppContext);

    return (
        <React.Fragment>
            <Container>
                <Segment style={{background: "#555555", margin: "5px"}}>
                    <Button color='red' inverted as='a' style={{float: "right"}}
                            onClick={appState.actions.logout}>Logout</Button>
                    <Label color='grey' ribbon>
                        User
                    </Label>
                    <br/>
                    <h4>{appState.user.first_name + " " + appState.user.last_name + " (" + appState.user.username + ")"}</h4>
                    <Label color='orange' ribbon>
                        Connections
                    </Label>
                    <br/>
                    {/*<Statistic.Group>*/}
                    <Statistic inverted>
                        <Statistic.Value>{getConnectionsCount(appState.connections)}</Statistic.Value>
                        <Statistic.Label>Total</Statistic.Label>
                    </Statistic>
                    <Statistic inverted>
                        <Statistic.Value><Icon name='angle double right'/></Statistic.Value>
                    </Statistic>
                    <Statistic color='blue' inverted>
                        <Statistic.Value>{getConnectionsCount(appState.connections, "rdp")}</Statistic.Value>
                        <Statistic.Label>RDP</Statistic.Label>
                    </Statistic>
                    <Statistic color='green' inverted>
                        <Statistic.Value>{getConnectionsCount(appState.connections, "ssh")}</Statistic.Value>
                        <Statistic.Label>SSH</Statistic.Label>
                    </Statistic>
                    <Statistic color='teal' inverted>
                        <Statistic.Value>{getConnectionsCount(appState.connections, "vnc")}</Statistic.Value>
                        <Statistic.Label>VNC</Statistic.Label>
                    </Statistic>
                    {/*</Statistic.Group>*/}
                    <br/>
                    <Label color='green' ribbon>
                        Access tickets
                    </Label>
                    <br/>

                    <Statistic color="green" inverted>
                        <Statistic.Value>{appState.tickets.filter(t => t.user.id === appState.user.id).length}</Statistic.Value>
                        <Statistic.Label>Personal</Statistic.Label>
                    </Statistic>
                    <Statistic color="yellow" inverted>
                        <Statistic.Value>{appState.tickets.filter(t => t.user.id === appState.user.id && t.user.id !== t.author.id).length}</Statistic.Value>
                        <Statistic.Label>Received</Statistic.Label>
                    </Statistic>
                    <Statistic color="red" inverted>
                        <Statistic.Value>{appState.tickets.filter(t => t.author.id === appState.user.id && t.user.id !== t.author.id).length}</Statistic.Value>
                        <Statistic.Label>Shared</Statistic.Label>
                    </Statistic>


                    <Divider/>

                    <Label as='a' target="_blank" href="https://guacozy.readthedocs.io" image style={{float: "right"}}>
                        <img src='favicon.ico' alt="logo"/>
                        Guacozy
                        <Label.Detail>{process.env.REACT_APP_VERSION}</Label.Detail>
                    </Label>
                    <br/>
                </Segment>
            </Container>
        </React.Fragment>
    );
}

function getConnectionsCount(tree, protocol) {
    let filter = () => true;

    if (protocol) {
        filter = (node) => node.protocol === protocol;
    }

    if (tree) {
        return tree.reduce(function (total, node) {
            return total + ((!node.isFolder && filter(node)) ? 1 : 0) + getConnectionsCount(node.children, protocol);
        }, 0)
    }
    return 0;
}

export default Welcome;