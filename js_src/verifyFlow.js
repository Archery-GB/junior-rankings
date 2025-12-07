import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';

import useLoadData from './hooks/useLoadData';
import Card from './layout/Card';

const VerifyFlow = () => {
    const [toVerify, setToVerify] = useState(null);
    const { error, loading, load } = useLoadData('scores-to-verify')

    const loadData = (e) => {
        e.preventDefault();
        load().then((data) => {
            console.log(data);
            setToVerify(data);
        });
    };

    return (
        <Card>
            <h4>Verify submitted scores</h4>
            <p>Administrator flow to verify or reject scores submitted by athletes.</p>
            { error && <p className="error">{ error.message }</p> }
            { !toVerify && <input type="submit" value="Start" onClick={ loadData } disabled={ loading } /> }
            { toVerify && toVerify.length }
        </Card>
    );
};

const verifyFlowApp = document.getElementById('app-verify-flow');

if (verifyFlowApp) {
    const root = createRoot(verifyFlowApp);
    root.render(<VerifyFlow />);
}
