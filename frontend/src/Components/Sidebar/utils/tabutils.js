import React from 'react';

// given uuid of ticket and name of tab constructs an element with context menu handler
export const tabNameElement = (ticketUUID, tabName) => (
    <span>{tabName}</span>
);