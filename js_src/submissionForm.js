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

    const submit = (e) => {
        e.preventDefault();
        onComplete({ agbNo });
    };

    return (
        <>
            <p>We are currently in the score submission phase. Please enter your Archery GB number below to start checking your scores.</p>
            <form onSubmit={ submit }>
                <input type="number" className="standout" name="agb_number" placeholder="Archery GB Number" onChange={ (e) => setAgbNo(e.target.value) } />
                <input disabled={ !agbNo } type="submit" value="Start" />
            </form>
        </>
    );
};


const Step1 = ({ agbNo, onComplete }) => {
    return (
        <>
            <h4>Step 1: Check your details</h4>
            <dl>
                <dt>Archery GB Number</dt>
                <dd>{ agbNo }</dd>
                <dt>Name</dt>
                <dd>Matilda Clayson</dd>
                <dt>Year of Birth</dt>
                <dd>2010</dd>
                <dt>Gender</dt>
                <dd>Female</dd>
                <dt>Age class</dt>
                <dd>U16</dd>
                <dt>Division</dt>
                <dd>Recurve</dd>
            </dl>
            <p className="help">Something not quite right? Please contact us.</p>
            <input type="submit" value="Confirm" onClick={ onComplete } />
        </>
    );
};


const Step2 = ({ onComplete }) => {
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
            
            <h5>Junior National Outdoor Championships Day 1</h5>
            <dl>
                <dt>Round</dt>
                <dd>AGB 900 50</dd>
                <dt>Score</dt>
                <dd>816</dd>
                <dt>Handicap</dt>
                <dd>37</dd>
            </dl>

            <hr />
            
            <h5>Junior National Outdoor Championships Day 2</h5>
            <dl>
                <dt>Round</dt>
                <dd>Windsor 50</dd>
                <dt>Score</dt>
                <dd>914</dd>
                <dt>Handicap</dt>
                <dd>42</dd>
            </dl>
            
            <hr />

            <h5>Best handicap total</h5>
            <p>Your best three scores give an aggregate handicap of <strong>120</strong>.</p>

            <p className="help">Something not quite right? Please contact us.</p>

            <input type="submit" value="Confirm scores" onClick={ () => onComplete({}, 4) } />
            <input type="submit" value="Add more scores" onClick={ onComplete } />
        </>
    );
};


const Step3 = ({ onComplete }) => {
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
            <select>
                <option>SCAS Regional Championships</option>
            </select>
            <label>Round</label>
            <select>
                <option>Windsor 500</option>
            </select>
            <label>Score</label>
            <input type="text" value="896"/>
            <label>Handicap</label>
            <p>42</p>
            <input type="submit" value="Add score" />
            <hr />
            <h4>Scores so far</h4>
            <h5>Junior National Outdoor Championships Day 1</h5>
            <dl>
                <dt>Round</dt>
                <dd>AGB 900 50</dd>
                <dt>Score</dt>
                <dd>816</dd>
                <dt>Handicap</dt>
                <dd>37</dd>
            </dl>
            <p>…</p>
            <hr />

            <h5>Best handicap total</h5>
            <p>Your best three scores give an aggregate handicap of <strong>120</strong>.</p>

            <p className="help">Something not quite right? Please contact us.</p>

            <input type="submit" value="Confirm scores" onClick={ onComplete } />
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

    return (
        <Card>
            <Current onComplete={ nextStep } { ...params } />
        </Card>
    );
};

if (submissionFormApp) {
    const root = createRoot(submissionFormApp);
    root.render(<SubmissionFormManager />);
}
