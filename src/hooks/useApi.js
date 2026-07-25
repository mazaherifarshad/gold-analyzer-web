import { useEffect, useState } from "react";
import api from "../services/api";

export default function useApi(endpoint, interval = 10000) {

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const load = async () => {

        try {

            const res = await api.get(endpoint);

            setData(res.data);

            setError("");

        } catch (err) {

            console.error(err);

            setError("Connection Error");

        } finally {

            setLoading(false);

        }

    };

    useEffect(() => {

        load();

        const timer = setInterval(load, interval);

        return () => clearInterval(timer);

    }, []);

    return {
        data,
        loading,
        error,
        refresh: load
    };

}