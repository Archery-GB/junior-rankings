import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';

import useLoadData from './hooks/useLoadData';
import Card from './layout/Card';


const ScoreRow = ({ score, accept, onChange }) => {
    const acceptScore = (e) => {
        e.preventDefault();
        onChange(true);
    };
    const rejectScore = (e) => {
        e.preventDefault();
        onChange(false);
    };

    let buttons = null;
    if (score.verified) {
        buttons = <button className="small" disabled>Verified</button>;
    } else {
        buttons = <span>
            <button className={ "small " + (accept === true ? "active" : "" ) } onClick={ acceptScore }>Accept</button>&nbsp;
            <button className={ "small " + (accept === false ? "active" : "" ) } onClick={ rejectScore }>Reject</button>
        </span>;
    }

    return <>
        <h5>
            { score.event }
            { buttons }
        </h5>
        <dl>
            <dt>Date</dt>
            <dd>{ new Date(score.date).toDateString() }</dd>
            <dt>Round</dt>
            <dd>{ score.round }</dd>
            <dt>Score</dt>
            <dd>{ score.score }</dd>
            <dt>Handicap</dt>
            <dd>{ score.handicap }</dd>
        </dl>
    </>;
};


const ScoreChecker = ({ athlete, scores, newScores }) => {
    const [toSave, setToSave] = useState({});

    const allScores = [...scores, ...newScores].sort((s1, s2) => s1.handicap - s2.handicap);

    let scoreSection = null;
    if (allScores.length) {
        const scoreRows = allScores.map(score => {
            const setAccept = (accept) => {
                const newToSave = { ...toSave };
                newToSave[score.id] = accept;
                setToSave(newToSave);
            };
            return <ScoreRow key={ score.id } score={ score } accept={ toSave[score.id] } onChange={ setAccept } />
        });

        scoreSection = <>
            <h5>Scores</h5>
            { scoreRows }
        </>;
    }

    const acceptedLength = Object.keys(toSave).length;
    console.log(acceptedLength, newScores.length);
    return <>
        <h4>{ athlete.name }</h4>
        <dl>
            <dt>Gender</dt> <dd>{ athlete.gender }</dd>
            <dt>Class</dt> <dd>{ athlete.age }</dd>
            <dt>Division</dt> <dd>{ athlete.division }</dd>
            <dt>Checked scores</dt> <dd>{ scores.length }</dd>
            <dt>Submitted scores</dt> <dd>{ newScores.length }</dd>
        </dl>
        { scoreSection }
        { acceptedLength === newScores.length && <input type="submit" value="Save scores" /> }
    </>;
};


const VerifyFlow = () => {
    const [toVerify, setToVerify] = useState(null);
    const [current, setCurrent] = useState(null);
    const [next, setNext] = useState(null);
    const { error, loading, load } = useLoadData('scores-to-verify')
    const athleteLoadData = useLoadData('submission-details');
    const errorAthlete = athleteLoadData.error;
    const loadingAthlete = athleteLoadData.loading;
    const loadAthlete = athleteLoadData.load;

    const loadData = (e) => {
        e.preventDefault();
        load().then((data) => {
            setToVerify(data.toVerify)
            if (data.toVerify.length) {
                setNext(data.toVerify[0]);
            }
        });
    };

    const onLoadAthlete = (id) => {
        return (e) => {
            e.preventDefault();
            loadAthlete({ id }).then((data) => {
                window.scrollTo({top: 0});
                setCurrent({
                    athlete: next,
                    scores: data.scores,
                    newScores: data.newScores,
                });
                const index = toVerify.map(a => a.id).indexOf(id);
                setNext(toVerify[index + 1]);
            });
        };
    };

    let scoreCheck = null;
    if (current) {
        scoreCheck = <ScoreChecker { ...current } key={ current.athlete.id } />
    }

    let nextStep = null;
    if (toVerify && toVerify.length) {
        nextStep = <>
            <h4>Progress</h4>
            <p>There are { toVerify.length } submissions left to verify.</p>
            <input type="submit" value={ "Next: " + next.name } onClick={ onLoadAthlete(next.id) } disabled={ loadingAthlete } />
        </>;
    }

    return (
        <Card>
            <h3>Verify submitted scores</h3>
            <p>Administrator flow to verify or reject scores submitted by athletes.</p>
            { error && <p className="error">{ error.message }</p> }
            { errorAthlete && <p className="error">{ errorAthlete.message }</p> }
            { !toVerify && <input type="submit" value="Start" onClick={ loadData } disabled={ loading } /> }
            { scoreCheck }
            { nextStep }
        </Card>
    );
};

const verifyFlowApp = document.getElementById('app-verify-flow');

if (verifyFlowApp) {
    const root = createRoot(verifyFlowApp);
    root.render(<VerifyFlow />);
}
