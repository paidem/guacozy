import React, {useCallback, useEffect, useRef, useState} from 'react';
import Guacamole from 'guacamole-common-js'
import {Button, Dimmer, Divider, Loader} from "semantic-ui-react";
import {GUACAMOLE_STATUS, GUACAMOLE_CLIENT_STATES} from "./const";

/***
 *
 * @param wspath - path of websocket with guacadmin server
 * @param tabIndex - needed to make containing div focusable
 * @param controlSize - bool to specify if this GuacViewer should try to control size (send resize commands)
 * @param screenSize - if set to null, uses automatic adjustment, otherwise uses {width, height} properties from object
 * @param node - FlexLayout node. Let's us subscribe to event
 * @param nodeSelectCallback - Callback to call when hosting div is clicked
 * @param nodeDeleteCallback - Callback to call when we need to delete hosting us
 * @returns {*}
 * @constructor
 */
function GuacViewer({wspath, tabIndex, controlSize = true, controlInput = true, screenSize = null, node, nodeSelectCallback, nodeDeleteCallback}) {
    const displayRef = useRef(null);
    const guacRef = useRef(null);
    const connectParamsRef = useRef({});
    const scale = useRef(1);
    const demandedScreenSize = useRef(0);

    // Timer which controls timeot for display size update
    const updateDisplaySizeTimerRef = useRef(0);


    const [clientState, setClientState] = useState(0);
    const [errorMessage, setErrorMessage] = useState(null);

    const getConnectionString = () => {
        let params = connectParamsRef.current;
        return Object.keys(params).map((key) => {
            if (Array.isArray(params[key])) {
                return params[key].map(item => encodeURIComponent(key) + '=' + encodeURIComponent(item)).join('&')
            }
            return encodeURIComponent(key) + '=' + encodeURIComponent(params[key])
        }).join('&');
    };

    // updates scale factor given new actual display width/height
    const rescaleDisplay = useCallback(() => {
        // get current width/height of connection
        let remoteDisplayWidth = guacRef.current.getDisplay().getWidth();
        let remoteDisplayHeight = guacRef.current.getDisplay().getHeight();

        if (!displayRef.current) {
            return;
        }

        let newWidth = displayRef.current.clientWidth;
        let newHeight = displayRef.current.clientHeight;

        // calculate which scale should we use - width or height, in order to see all of remote display
        let newScale = Math.min(newWidth / remoteDisplayWidth, newHeight / remoteDisplayHeight, 1);

        guacRef.current.getDisplay().scale(newScale);
        scale.current = newScale;
    }, []);

    // Display size update handler, currently implement onli logging to console
    const updateDisplaySize = useCallback((timeout, widthparam, heightparam) => {

        if (!guacRef.current)
            return;

        // If we have resize scheduled - cancel it, because we received new insructions
        if (updateDisplaySizeTimerRef.current) {
            clearTimeout(updateDisplaySizeTimerRef.current);
        }

        let newDisplayWidth = 0;
        let newDisplayHeight = 0;

        // Timeout to 500 ms, so that size is updated 0.5 second after resize ends
        updateDisplaySizeTimerRef.current = setTimeout(() => {

            // if we are provided with widthparam/heightparam upfront - use them
            if (widthparam > 0 && heightparam > 0) {
                newDisplayWidth = widthparam;
                newDisplayHeight = heightparam;
            } else if (displayRef.current) {
                // otherwise we can measure client size of display element and use it
                // this is usually needed when we are connecting

                newDisplayWidth = displayRef.current.clientWidth;
                newDisplayHeight = displayRef.current.clientHeight;
            }

            // save new width/height for reconnect purposes
            connectParamsRef.current.width = newDisplayWidth;
            connectParamsRef.current.height = newDisplayHeight;

            if (newDisplayWidth > 1 && newDisplayHeight > 1) {
                if (controlSize) {
                    if (demandedScreenSize.current) {
                        guacRef.current.sendSize(demandedScreenSize.current.width, demandedScreenSize.current.height);
                    } else {
                        guacRef.current.sendSize(newDisplayWidth, newDisplayHeight);
                    }

                    // we sent resize command and possiblty resolution will be update
                    // take a timeout to see the updated resolution of GuacamoleClient dispalay
                    setTimeout(() => {
                        rescaleDisplay()
                    }, 500);
                } else {
                    // We do not have control over display size, it means GuacamoleClient display will not change
                    // so we can rescale display right away
                    rescaleDisplay();
                }
            }

        }, timeout > 0 ? timeout : 500);
    }, [controlSize, rescaleDisplay]);


    // Focuses Guacamole Client Display element if it's parent element has been clicked,
    // because div with GuacamoleClient inside otherwise does not focus.
    const parentOnClickHandler = () => {
        displayRef.current.focus();

        // nodeSelectCallback - make the node hosting this component active if this component is clicked
        if (nodeSelectCallback) {
            nodeSelectCallback(node._attributes.id);
        }
    };

    useEffect(() => {

        // Subscribe to FlexLayout node visibility event
        // if visibility has changed, and element became visible, there is a great chance it became visible because
        // of tab beeing activated. That is a nice occasion to focus on tab.
        // Timeout is needed because "visibility" event is fired before the tab name gets focus,
        // so we schedule 100 ms after event and take back focus from tab name element
        const visibilityChangedCallback = (p) => {
            if (p.visible) {
                setTimeout(() => {
                    displayRef.current.focus();
                    updateDisplaySize(50);
                }, 100);
            }
        };
        node.setEventListener("visibility", visibilityChangedCallback);

        // Subscribe to FlexLayout node resize event.
        // This will provide use updated size of visible recangle
        // Event is fired before actual resize happens, and provides with new dimensions (rect)
        const updateDisplaySizeCallback = (rect) => {
            updateDisplaySize(0, rect.width, rect.height);
        };

        node.setEventListener("resize", updateDisplaySizeCallback);

        // Specify how to cleanup after this effect
        return () => {
            node.removeEventListener("visibility", visibilityChangedCallback);
            node.removeEventListener("resize", updateDisplaySizeCallback);
        }

    }, [node, updateDisplaySize]);


    // Main effect which constructs GuacamoleClient
    // should reaaaly be run only once
    useEffect(() => {
        // Determine websocket URI
        const protocolPrefix = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let {host} = window.location;
        let webSocketFullUrl = `${protocolPrefix}//${host}${wspath}`;

        guacRef.current = new Guacamole.Client(new Guacamole.WebSocketTunnel(webSocketFullUrl));

        displayRef.current.appendChild(guacRef.current.getDisplay().getElement());

        // Error handler
        guacRef.current.onerror = function (error) {
            let msg = error.message;

            if (GUACAMOLE_STATUS[error.code]) {
                msg = <p>
                    {error.message}<br/>
                    {GUACAMOLE_STATUS[error.code].name}<br/>
                    {GUACAMOLE_STATUS[error.code].text}
                </p>
            }

            setErrorMessage(msg);
        };

        // Update state, component knows when to render faders, "Loading..." and so on
        guacRef.current.onstatechange = (newState) => {
            setClientState(newState);
        };

        // Setup connection parameters, like resolution and supported audio types
        let connectionParams = {
            audio: []
        };

        // if current instance is allowed to control remote display size - include window size in connection info
        if (controlSize) {
            connectionParams.width = displayRef.current.clientWidth;
            connectionParams.height = displayRef.current.clientHeight;
        }

        let supportedAudioTypes = Guacamole.AudioPlayer.getSupportedTypes();
        if (supportedAudioTypes.length > 0) {
            connectionParams.audio = supportedAudioTypes.map(item => item + ";rate=44100,channels=2")
        }

        // Set connection parameters as we will use them later to reconnect
        connectParamsRef.current = connectionParams;

        // Everything has been setup - we can initiate connection
        guacRef.current.connect(getConnectionString());

        // Specify how to clean up after this effect:
        return function cleanup() {
            // Disconnect Guacamole Client, so server know'w we don't need any updates and teminates connection
            // to server
            guacRef.current.disconnect();
        };

    }, [wspath, updateDisplaySize, controlSize]);

    // This effect fires when "screenSize" prop has changed, which mean either
    // demanded resolution was change of set to Auto
    useEffect(() => {
        demandedScreenSize.current = screenSize;

        if (screenSize) {
            updateDisplaySize(100, demandedScreenSize.current.width, demandedScreenSize.current.height)
        } else {
            updateDisplaySize();
        }
    }, [updateDisplaySize, screenSize]);

    // This effect creates Guacamole.Keyboard / Guacamole.Mouse on current display element and binds callbacks
    // to current guacamole client
    useEffect(() => {
        // don't bind to events if we know this input will not be accepted at server side
        if (!controlInput) {
            return;
        }

        // Keyboard
        let keyboard = new Guacamole.Keyboard(displayRef.current);

        const fixKeys = (keysym) => {
            // 65508 - Right Ctrl
            // 65507 - Left Ctrl
            // somehow Right Ctrl is not sent, so send Left Ctrl instead
            if (keysym === 65508) return 65507;

            return keysym
        };

        keyboard.onkeydown = function (keysym) {
            guacRef.current.sendKeyEvent(1, fixKeys(keysym));
        };

        keyboard.onkeyup = function (keysym) {
            guacRef.current.sendKeyEvent(0, fixKeys(keysym));
        };

        // Mouse
        let mouse = new Guacamole.Mouse(displayRef.current);


        mouse.onmousemove = function (mouseState) {
            mouseState.x = mouseState.x / scale.current;
            mouseState.y = mouseState.y / scale.current;
            guacRef.current.sendMouseState(mouseState);
        };

        mouse.onmousedown = mouse.onmouseup = function (mouseState) {
            guacRef.current.sendMouseState(mouseState);
        };


    }, [controlInput]);

    // Thi effect  binds to server side resize event
    useEffect(() => {
        if (!controlSize) {
            guacRef.current.getDisplay().onresize = (x, y) => {
                console.log(`Server changed size: ${x} x ${y}`);
                updateDisplaySize(0, x, y);
            }
        }
    }, [controlSize, updateDisplaySize]);

    // This effect manages subscribing to clipboard events to manage clipboard synchronization
    useEffect(() => {

        const handleServerClipboardChange = (stream, mimetype) => {
            // don't do anything if this is not active element
            if (document.activeElement !== displayRef.current)
                return;

            if (mimetype === "text/plain") {
                // stream.onblob = (data) => copyToClipboard(atob(data));
                stream.onblob = (data) => {
                    let serverClipboard = atob(data);
                    // we don't want action if our knowledge of server cliboard is unchanged
                    // and also don't want to fire if we just selected several space character accidentaly
                    // which hapens often in SSH session
                    if (serverClipboard.trim() !== "") {
                        // put data received form server to client's clipboard
                        navigator.clipboard.writeText(serverClipboard);

                    }
                }
            } else {
                // Haven't seen those yet...
                console.log("Unsupported mime type:" + mimetype)
            }
        };

        // Read client's clipboard
        const onFocusHandler = () => {
            // when focused, read client clipboard text
            navigator.clipboard.readText().then(
                (clientClipboard) => {
                    let stream = guacRef.current.createClipboardStream("text/plain", "clipboard");
                    setTimeout(() => {
                        // remove '\r', because on pasting it becomes two new lines (\r\n -> \n\n)
                        stream.sendBlob(btoa(unescape(encodeURIComponent(clientClipboard.replace(/[\r]+/gm, "")))));
                    }, 200)
                }
            )
        };

        // add handler only when navigator clipboard is available
        if (navigator.clipboard) {
            displayRef.current.addEventListener("focus", onFocusHandler);
            guacRef.current.onclipboard = handleServerClipboardChange;
        }
    }, []);

    const reconnect = () => {
        setErrorMessage(null);
        guacRef.current.connect(getConnectionString());
    };

    return (
        <React.Fragment>
            <div ref={displayRef}
                 onClick={parentOnClickHandler}
                 style={{
                     width: "100%",
                     height: "100%",
                     overflow: "hidden",
                     cursor: "none"
                 }}
                 tabIndex={tabIndex}
            />
            <Dimmer
                active={clientState < GUACAMOLE_CLIENT_STATES.STATE_CONNECTED}>
                <Loader>Connection</Loader>
            </Dimmer>

            <Dimmer
                active={clientState > GUACAMOLE_CLIENT_STATES.STATE_CONNECTED}>
                <Loader><p>Session disconnected</p>
                    {errorMessage &&
                    <span style={{color: "red"}}>Error: {errorMessage}</span>}
                    <Divider/>

                    <Button inverted color='green' onClick={reconnect}>
                        Reconnect
                    </Button>
                    <Button inverted color='red'
                            onClick={() => nodeDeleteCallback(node._attributes.id)}>
                        Close tab
                    </Button>
                </Loader>
            </Dimmer>
        </React.Fragment>
    );
}

export default GuacViewer;

