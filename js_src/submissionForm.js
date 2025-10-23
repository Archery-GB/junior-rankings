import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';


const submissionFormApp = document.getElementById('app-submission-form');


const Card = ({ children }) => {
    return (
        <div className="card">
            { children }
        </div>
    );
};


const Intro = ({ onComplete }) => {
    const [agbNo, setAgbNo] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const submit = (e) => {
        e.preventDefault();
        setLoading(true);
        var url = new URL('/api/athlete-details/', window.location.href);
        var params = { agb_number: agbNo };
        url.search = new URLSearchParams(params).toString();
        fetch(url).then((response) => response.json()).then((data) => {
            setLoading(false);
            if (data.error) {
                console.error(data.error);
                setError({ agbNo });
                return;
            }
            onComplete({ athlete: data });
        });
    };

    var submitLabel = "Start";
    if (loading) submitLabel = "Loading";

    return (
        <>
            <p>We are currently in the score submission phase. Please enter your Archery GB number below to start checking your scores.</p>
            { error && <p className="error">We cannot find a junior archer for the membership number { error.agbNo }.</p> }
            <form onSubmit={ submit }>
                <input type="number" className="standout" name="agb_number" placeholder="Archery GB Number" onChange={ (e) => setAgbNo(e.target.value) } />
                <input disabled={ !agbNo || loading } type="submit" value={ submitLabel }/>
            </form>
        </>
    );
};


const Step1 = ({ athlete, onComplete }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const submit = (e) => {
        e.preventDefault();
        setLoading(true);
        var url = new URL('/api/athlete-scores/', window.location.href);
        var params = { agb_number: athlete.agbNo };
        url.search = new URLSearchParams(params).toString();
        fetch(url).then((response) => response.json()).then((data) => {
            setLoading(false);
            if (data.error) {
                console.error(data.error);
                setError({ agbNo: athlete.agbNo });
                return;
            }
            onComplete({ scores: data.scores });
        });
    };

    return (
        <>
            <h4>Step 1: Check your details</h4>
            <dl>
                <dt>Archery GB Number</dt>
                <dd>{ athlete.agbNo }</dd>
                <dt>Name</dt>
                <dd>{ athlete.name }</dd>
                <dt>Year of Birth</dt>
                <dd>{ athlete.year }</dd>
                <dt>Gender</dt>
                <dd>{ athlete.gender }</dd>
                <dt>Age class</dt>
                <dd>{ athlete.age }</dd>
                <dt>Division</dt>
                <dd>{ athlete.division }</dd>
            </dl>
            <p className="help">Something not quite right? Please contact us.</p>
            <input type="submit" value="Confirm" onClick={ submit } />
        </>
    );
};


const ScoreRow = ({ score }) => {
    return (
        <>
            <h5>{ score.event }</h5>
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
            <hr />
        </>
    );
};


const Step2 = ({ athlete, scores, onComplete }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const scoreRows = scores.map((score) => <ScoreRow score={ score } key={ score.eventId } />);

    const hasThree = scores.length >= 3;

    var bestHandicap = null;
    if (hasThree) {
        bestHandicap = scores.slice(0, 3).map((score) => score.handicap).reduce((a, b) => a+b);
    }

    const onAddScores = (e) => {
        e.preventDefault();
        setLoading(true);
        var url = new URL('/api/available-events/', window.location.href);
        var params = { agb_number: athlete.agbNo };
        url.search = new URLSearchParams(params).toString();
        fetch(url).then((response) => response.json()).then((data) => {
            setLoading(false);
            if (data.error) {
                console.error(data.error);
                setError({ agbNo: athlete.agbNo });
                return;
            }
            onComplete({ events: data.events });
        });
    };

    return (
        <>
            <h4>Step 2: Check scores automatically imported</h4>
            <p>
            We have automatically included scores from a range of competitions for
            which we received digital data. If your best scores are already included,
            you don't need to do anything. If you have better scores from another
            event, you can submit them on the next page.
            </p>
            <hr />

            { scoreRows }

            <h5>Ranking total</h5>
            { bestHandicap &&
                <p>Your best three scores give an aggregate handicap of <strong>{ bestHandicap }</strong>.</p> ||
                <p>You require three qualifying scores to obtain a ranking. Please add some more.</p>
            }

            <p className="help">Something not quite right? Please contact us.</p>

            { bestHandicap && <input type="submit" value="Confirm scores" onClick={ () => onComplete({}, 4) } /> }
            <input type="submit" value="Add more scores" onClick={ onAddScores } />
        </>
    );
};


const Step3 = ({ events, scores, addScore, onComplete }) => {
    const [addedScores, setAddedScores] = useState([]);
    const [currentEvent, setCurrentEvent] = useState("");
    const [currentRound, setCurrentRound] = useState("");
    const [currentScore, setCurrentScore] = useState("");
    const [hc, setHc] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const scoreRows = scores.map((score) => <ScoreRow score={ score } key={ score.eventId } />);

    const hasThree = scores.length >= 3;

    var bestHandicap = null;
    if (hasThree) {
        bestHandicap = scores.slice(0, 3).map((score) => score.handicap).reduce((a, b) => a+b);
    }

    const eventOptions = events.map((ev) => {
        return <option value={ ev.identifier } key={ ev.identifier }>{ ev.name }</option>;
    })
    let ev = null;
    let rnd = null;
    let roundOptions = null;

    if (currentEvent) {
        ev = events.find((e) => e.identifier === currentEvent);
        roundOptions = ev.rounds.map((r) => {
            return <option value={ r.codename } key={ r.codename }>{ r.name }</option>;
        })
    }
    if (currentRound) {
        rnd = ev.rounds.find((r) => r.codename === currentRound);
    }

    const selectEvent = (e) => {
        setError(null);
        setCurrentEvent(e.target.value);
        setCurrentRound("");
        setCurrentScore("");
        setHc(null);
    }
    const selectRound = (e) => {
        setError(null);
        setCurrentRound(e.target.value);
        setCurrentScore("");
        setHc(null);
    }
    const setScore = (e) => {
        setError(null);
        setCurrentScore(e.target.value);
        setHc(null);
        setLoading(true);
        var url = new URL('/api/handicap/', window.location.href);
        var params = { round: currentRound, score: e.target.value };
        url.search = new URLSearchParams(params).toString();
        fetch(url).then((response) => response.json()).then((data) => {
            setLoading(false);
            if (data.error) {
                console.error(data.error);
                setError({ message: "Invalid score" });
                return;
            }
            setHc(data.handicap);
        });
    }
    const onAddScore = (e) => {
        e.preventDefault();
        setError(null);
        setCurrentEvent("");
        setCurrentRound("");
        setCurrentScore("");
        setHc(null);

        console.log(scores);
        const newScore = {
            date: ev.date,
            event: ev.name,
            eventId: ev.identifier,
            handicap: hc,
            round: rnd.name,
            score: currentScore,
        };
        addScore(newScore);
    }

    return (
        <>
            <h4>Step 3: Add additional scores</h4>
            <p>
            Scores must have been shot during 2025 at a World or UK Record status
            competition, and they must have been on a qualifying round for your age
            group and division.
            </p>
            <hr />
            <h4>Add a score</h4>
            <label>Event</label>
            <select value={ currentEvent } onChange={ selectEvent }>
                <option>Select event…</option>
                { eventOptions }
            </select>
            { currentEvent &&  
                <>
                    <label>Round</label>
                    <select value={ currentRound } onChange={ selectRound }>
                        <option>Select round…</option>
                        { roundOptions }
                    </select>
                    { currentRound &&
                        <>
                            <label>Score</label>
                            <input type="text" value={ currentScore } onChange={ setScore } />
                            { hc && 
                                <>
                                    <label>Handicap</label>
                                    <p>{ hc }</p>
                                    <input type="submit" value="Add score" onClick={ onAddScore } />
                                </>
                            }
                        </>
                    }
                </>
            }
            { error && <p className="error">{ error.message }</p>}
            <hr />
            <h4>Scores so far</h4>
            { scoreRows }

            <h5>Ranking total</h5>
            { bestHandicap &&
                <p>Your best three scores give an aggregate handicap of <strong>{ bestHandicap }</strong>.</p> ||
                <p>You require three qualifying scores to obtain a ranking. Please add some more.</p>
            }

            <p className="help">Something not quite right? Please contact us.</p>

            { bestHandicap && <input type="submit" value="Confirm scores" onClick={ onComplete } /> }
        </>
    );
};


const Outro = ({ onComplete }) => {
    return (
        <>
            <h4>Thank you!</h4>
            <p>Your scores will be verified and the final rankings will be published in November.</p>
            <a onClick={ () => onComplete({}, 0) }>Back to start</a>
        </>
    );
};


const SubmissionFormManager = () => {
    const [step, setStep] = useState(0);
    const [params, setParams] = useState({});

    const steps = [
        Intro,
        Step1,
        Step2,
        Step3,
        Outro,
    ];
    const Current = steps[step];
    if (!Current) {
        console.error('Unknown step', step);
        return <h1>Error</h1>;
    }

    const nextStep = (newParams, nextStep=null) => {
        if (nextStep !== null) {
            setStep(nextStep);
        } else {
            setStep(step + 1);
        }
        setParams({ ...params, ...newParams });
    };

    const addScore = (newScore) => {
        let scores = [newScore, ...params.scores];
        scores.sort((a, b) => a.handicap - b.handicap);
        setParams({ ...params, scores });
    };

    return (
        <Card>
            <Current onComplete={ nextStep } addScore={ addScore } { ...params } />
        </Card>
    );
};

if (submissionFormApp) {
    const root = createRoot(submissionFormApp);
    root.render(<SubmissionFormManager />);
}
