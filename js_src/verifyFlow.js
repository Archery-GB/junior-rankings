import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';

import Cookies from 'cookies-js';

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


const ScoreChecker = ({ athlete, scores, newScores, onScoreSaved }) => {
    const [toSave, setToSave] = useState({});
    const [saved, setSaved] = useState(false);

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

    const save = (e) => {
        e.preventDefault();
        var url = new URL('/api/verify-scores/', window.location.href);
        const data = { scores: Object.entries(toSave).map(row => { return { id: row[0], accept: row[1] } }),  id: athlete.id };
        const csrf = Cookies.get('csrftoken');
        fetch(url, {
            method: "POST",
            body: JSON.stringify(data),
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
            },
            redirect: 'follow',
        }).then((response) => {
            if (response.status !== 200) {
                console.error("Something went wrong");
                window.scrollTo({top: 0});
                return;
            }
            setSaved(true);
            onScoreSaved();
        });
    }

    const acceptedLength = Object.keys(toSave).length;
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
        { acceptedLength === newScores.length && <input type="submit" value={ saved ? "Saved" : "Save scores" } onClick={ save } disabled={ saved } /> }
    </>;
};


const VerifyFlow = () => {
    const [toVerify, setToVerify] = useState(null);
    const [current, setCurrent] = useState(null);
    const [next, setNext] = useState(null);
    const [count, setCount] = useState(null);
    const { error, loading, load } = useLoadData('scores-to-verify')
    const athleteLoadData = useLoadData('submission-details');
    const errorAthlete = athleteLoadData.error;
    const loadingAthlete = athleteLoadData.loading;
    const loadAthlete = athleteLoadData.load;

    const loadData = (e) => {
        e.preventDefault();
        load().then((data) => {
            setToVerify(data.toVerify)
            setCount(data.toVerify.length);
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

    const onScoreSaved = () => {
        setCount(count - 1);
    }

    let scoreCheck = null;
    if (current) {
        scoreCheck = <ScoreChecker { ...current } key={ current.athlete.id } onScoreSaved={ onScoreSaved } />
    }

    let nextStep = null;
    if (toVerify && toVerify.length) {
        nextStep = <>
            <h4>Progress: { count } submissions to verify</h4>
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
