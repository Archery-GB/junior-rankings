import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';

import Cookies from 'cookies-js';


const submissionFormApp = document.getElementById('app-submission-form');


const Card = ({ children }) => {
    return (
        <div className="card">
            { children }
        </div>
    );
};


const Intro = ({ onComplete, toContact }) => {
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
            { error && <p className="error">We cannot find a junior archer for the membership number { error.agbNo }. This may be an error with the number, or could be that you didn't take part in any events we already have data for. Please use the contact link below and we'll be in touch.</p> }
            <form onSubmit={ submit }>
                <input type="number" className="standout" name="agb_number" placeholder="Archery GB Number" onChange={ (e) => setAgbNo(e.target.value) } />
                <input disabled={ !agbNo || loading } type="submit" value={ submitLabel }/>
            </form>

            <p className="help">Something not quite right? Please <a onClick={ toContact }>contact us</a>.</p>
        </>
    );
};


const Step1 = ({ athlete, onComplete, toContact }) => {
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
                <dt>Gender</dt>
                <dd>{ athlete.gender }</dd>
                <dt>Age class</dt>
                <dd>{ athlete.age }</dd>
                <dt>Division</dt>
                <dd>{ athlete.division }</dd>
            </dl>
            <p className="help">Something not quite right? Please <a onClick={ toContact }>contact us</a>.</p>
            <input type="submit" value="Confirm" onClick={ submit } />
        </>
    );
};


const ScoreRow = ({ score }) => {
    return (
        <>
            <h5>
                { score.event }
                { score.tempId && <button className="small" onClick={ score.remove }>Remove</button> }
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
            <hr />
        </>
    );
};


const Step2 = ({ athlete, scores, toContact, onComplete, submitFinal }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const scoreRows = scores.map((score) => <ScoreRow score={ score } key={ score.id } />);

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

            { !scoreRows.length &&
                <p className="error">We were not able to find any scores from our existing data for you. Please add some on the next page.</p>
            }

            { scoreRows }

            { scoreRows.length && <h5>Ranking total</h5> || null }
            { bestHandicap &&
                <p>Your best three scores give an aggregate handicap of <strong>{ bestHandicap }</strong>.</p> }
            { (scoreRows.length && !bestHandicap) &&
                <p>You require three qualifying scores to obtain a ranking. Please add some more.</p>
            || null }

            <p className="help">Something not quite right? Please <a onClick={ toContact }>contact us</a>.</p>

            { bestHandicap && <input type="submit" value="Confirm scores" onClick={ submitFinal } /> }
            <input type="submit" value="Add more scores" onClick={ onAddScores } />
        </>
    );
};


const Step3 = ({ events, scores, addScore, toContact, onComplete, submitFinal }) => {
    const [addedScores, setAddedScores] = useState([]);
    const [currentEvent, setCurrentEvent] = useState("");
    const [currentRound, setCurrentRound] = useState("");
    const [currentScore, setCurrentScore] = useState("");
    const [hc, setHc] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const scoreRows = scores.map((score) => <ScoreRow score={ score } key={ score.id || score.tempId } />);

    const hasThree = scores.length >= 3;

    var bestHandicap = null;
    if (hasThree) {
        bestHandicap = scores.slice(0, 3).map((score) => score.handicap).reduce((a, b) => a+b);
    }

    const eventOptions = events.map((ev) => {
        const date = new Date(ev.date);
        return <option value={ ev.identifier } key={ ev.identifier }>{ date.getDate() }/{ date.getMonth() + 1 }/{ date.getFullYear() } - { ev.name }</option>;
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
        if (!e.target.value) {
            return;
        }
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

        const newScore = {
            date: ev.date,
            event: ev.name,
            eventId: ev.identifier,
            handicap: hc,
            round: rnd.name,
            roundCodename: rnd.codename,
            score: currentScore,
            tempId: new Date().toISOString(),
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
            <p className="help">
            This may show rounds of the correct family which were not available
            at the event. It will only show rounds eligible for your age group.
            </p>
            <hr />
            <h4>Add a score</h4>
            <label>Event</label>
            <select value={ currentEvent } onChange={ selectEvent }>
                <option value="">Select event…</option>
                { eventOptions }
            </select>
            { currentEvent &&  
                <>
                    <label>Round</label>
                    <select value={ currentRound } onChange={ selectRound }>
                        <option value="">Select round…</option>
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
            { scores.length &&
                <>
                    <h4>Scores so far</h4>
                    { scoreRows }

                    <h5>Ranking total</h5>
                    { bestHandicap &&
                        <p>Your best three scores give an aggregate handicap of <strong>{ bestHandicap }</strong>.</p> ||
                        <p>You require three qualifying scores to obtain a ranking. Please add some more.</p>
                    }
                </> || null
            }

            <p className="help">Something not quite right? Please <a onClick={ toContact }>contact us</a>.</p>

            { bestHandicap && <input type="submit" value="Confirm scores" onClick={ submitFinal } /> }
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


const Contact = ({ onComplete }) => {
    const [email, setEmail] = useState("");
    const [agbNo, setAgbNo] = useState("");
    const [message, setMessage] = useState("");
    const [complete, setComplete] = useState(false);

    const onSubmit = (e) => {
        e.preventDefault();
        setComplete(true);
        var url = new URL('/api/contact/', window.location.href);
        const data = { email, agbNo, message };
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
        });
    };

    return (
        <>
            <h4>Something not quite right?</h4>
            <p>This site is new for 2025 and has been developed by volunteers for the benefit of Archery GB. It probably doesn't cover every situation perfectly yet.</p>
            <p>If you've got a problem, please complete the below form and we will get back to you as soon as we can.</p>
            <hr />
            { !complete && <form onSubmit={ onSubmit }>
                <label>Your email</label>
                <input type="email" value={ email } onChange={ (e) => setEmail(e.target.value) } />
                <label>Archery GB Number</label>
                <input type="number" placeholder="Membership number of the archer concerned" value={ agbNo } onChange={ (e) => setAgbNo(e.target.value) } />
                <label>Message</label>
                <textarea value={ message } onChange={ (e) => setMessage(e.target.value) }/>
                <input type="submit" value="Contact" disabled={ !email || !agbNo || !message } />
            </form> }
            { complete &&
                <>
                    <h5>Message received</h5>
                    <p>Thank you, we will be in touch.</p>
                </>
            }
            <p>
                <a onClick={ () => onComplete({}, 0) }>Back to start</a>
            </p>
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
        Contact,
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
        window.scrollTo({top: 0});
    };

    const toContact = () => {
        nextStep({}, steps.length - 1);
    };

    const addScore = (newScore) => {
        newScore.remove = (e) => {
            e.preventDefault();
            const scores = params.scores.filter((s) => s.tempId !== newScore.tempId);
            setParams({ ...params, scores });
        };
        let scores = [newScore, ...params.scores];
        scores.sort((a, b) => a.handicap - b.handicap);
        setParams({ ...params, scores });
    };

    const submitFinal = (e) => {
        e.preventDefault();
        var url = new URL('/api/submit/', window.location.href);
        const data = { agbNo: params.athlete.agbNo, scores: params.scores.filter((s) => s.tempId).map((s) => {
            return {
                score: s.score,
                round: s.roundCodename,
                event: s.eventId,
            };
        })};
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
        }).then(() => {
            nextStep({}, steps.length - 2);
        });
    };

    return (
        <Card>
            <Current onComplete={ nextStep } toContact={ toContact } addScore={ addScore } submitFinal={ submitFinal } { ...params } />
        </Card>
    );
};

if (submissionFormApp) {
    const root = createRoot(submissionFormApp);
    root.render(<SubmissionFormManager />);
}
