import React, {useContext} from 'react';
import {Button, Divider, Segment} from "semantic-ui-react";
import {AppContext} from "../../Context/AppContext";
import Container from "semantic-ui-react/dist/commonjs/elements/Container";


function Welcome(props) {
    const [appState,] = useContext(AppContext);

    return (
        <React.Fragment>
            <Container>
                <Segment style={{background: "#555555", margin: "5px"}}>
                    Welcome, {appState.user.first_name + " " + appState.user.last_name + " (" + appState.user.username + ")"}

                    <Button color='red' inverted as='a' style={{float: "right"}}
                            onClick={appState.actions.logout}>Logout</Button>
                    <br/>
                    <br/>

                    <Divider/>


                    <Divider/>

                </Segment>
            </Container>
        </React.Fragment>
    );
}

export default Welcome;