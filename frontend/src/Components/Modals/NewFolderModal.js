import React, {useState, useContext, useRef} from 'react';
import {AppContext} from "../../Context/AppContext";
import {Button, Form, Header, Icon, Message, Modal} from "semantic-ui-react";
import ModalBase from "./ModalBase";

function NewFolderModal({handleClose, data}) {
    const [appState,] = useContext(AppContext);
    const [error, setError] = useState(null);

    const inputFieldRef = useRef(null);

    const submit = (e) => {
        e.preventDefault();

        let name = inputFieldRef.current.value;

        if (name !== data.name) {
            appState.api.createFolder({parendId: data.id, name: name})
                .then((response) => {
                    appState.actions.updateConnections();
                    handleClose();
                })
                .catch((error) => {
                    if (error.response && error.response.data && error.response.data.detail) {
                        setError(error.response.data.detail);
                    } else {
                        // objects are not valid react child and we render error verbatim, so to make it string, concat
                        setError("" + error);
                    }
                })
            ;
        }
    };

    return (
        <ModalBase handleClose={handleClose}>
            <Header icon='browser' content={'Create folder under ' + data.name}/>
            <Modal.Content>
                {error && <Message negative content={error}/>}
                <Form onSubmit={submit}>
                    <Form.Field>
                        <label>New folder name</label>
                        <input ref={inputFieldRef} autoFocus={true}/>
                    </Form.Field>
                    <Button type='submit' color='green'>
                        <Icon name='checkmark'/> Create
                    </Button>
                    <Button color='gray' onClick={handleClose}>
                        <Icon name='delete'/> Cancel
                    </Button>
                </Form>
            </Modal.Content>
        </ModalBase>
    );
}

export default NewFolderModal;