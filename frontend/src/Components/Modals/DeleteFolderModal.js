import React, {useContext, useState} from 'react';
import {AppContext} from "../../Context/AppContext";
import {Button, Header, Icon, Message, Modal} from "semantic-ui-react";
import ModalBase from "./ModalBase";

function DeleteFolderModal({handleClose, data}) {
    const [appState,] = useContext(AppContext);
    const [error, setError] = useState(null);

    const deleteFolder = (e) => {

        appState.api.deleteFolder({id: data.id})
            .then(() => {
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

    };

    return (
        <ModalBase handleClose={handleClose}>
            <Header icon='browser' content={'Delete folder ' + data.name + '?'}/>
            <Modal.Content>
                {error && <Message negative content={error}/>}
                <Button color='red' onClick={deleteFolder}>
                    <Icon name='checkmark'/> Delete
                </Button>
                <Button color='gray' onClick={handleClose}>
                    <Icon name='delete'/> Cancel
                </Button>
            </Modal.Content>
        </ModalBase>
    );
}

export default DeleteFolderModal;