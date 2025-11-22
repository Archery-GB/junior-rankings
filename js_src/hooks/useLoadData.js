import { useState } from 'react';

const useLoadData = (apiPath) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const load = (params = {}) => {
        var url = new URL('/api/' + apiPath + '/', window.location.href);
        url.search = new URLSearchParams(params).toString();
        const promise = fetch(url).then((response) => {
            setLoading(false);
            if (response.ok) {
                return response.json();
            }
            return response.json().catch(() => {
                const err = 'API ERROR: Non-JSON failed request with response code ' + response.status;
                throw new Error(err);
            });
        }).catch((err) => {
            console.error(err);
            setError(err);
        }).then((data) => {
            if (data.error) {
                setError({
                    message: data.error,
                    params,
                });
                console.error('API ERROR: Message: ', data);
            }
            return data;
        });

        return promise;
    }

    return {
        loading,
        error,
        load,
    };
};

export default useLoadData;
