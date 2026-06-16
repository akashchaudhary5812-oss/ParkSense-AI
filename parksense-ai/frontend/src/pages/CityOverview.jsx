import { useEffect, useState } from 'react'
import axios from 'axios'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import {
    Chart, BarElement, CategoryScale, LinearScale, PointElement,
    LineElement, ArcElement, Tooltip, Legend, Filler,
} from 'chart.js'
Chart.register(BarElement, CategoryScale, LinearScale, PointElement,
    LineElement, ArcElement, Tooltip, Legend, Filler)

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const KPI = ({ label, value, sub, color }) => (
    <div className="kpi-card" style={{ '--accent': color }}>
        <div className="kpi-label">{label}</div>
        <div className="kpi-value">{value}</div>
        <div className="kpi-sub">{sub}</div>
    </div>
)

export default function CityOverview() {
    const [hourly, setHourly] = useState([])
    const [stationStats, setStationStats] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            axios.get(`${API}/api/v1/violations/stats/hourly`),
            axios.get(`${API}/api/v1/violations/stats/by-station`),
        ]).then(([h, s]) => {
            setHourly(h.data)
            setStationStats(s.data)
        }).catch(() => {
            // Use dataset constants as fallback for demo
            setHourly(DEMO_HOURLY)
            setStationStats(DEMO_STATIONS)
        }).finally(() => setLoading(false))
    }, [])

    const hourlyData = {
        labels: hourly.map(r => `${String(r.hour).padStart(2, '0')}:00`),
        datasets: [{
            label: 'Violations',
            data: hourly.map(r => r.count),
            backgroundColor: hourly.map(r =>
                r.count > 30000 ? 'rgba(255,71,87,0.85)' :
                    r.count > 15000 ? 'rgba(255,127,80,0.75)' :
                        r.count > 5000 ? 'rgba(255,215,0,0.65)' : 'rgba(108,99,255,0.55)'
            ),
            borderRadius: 4,
        }],
    }

    const stationData = {
        labels: stationStats.slice(0, 10).map(r => r.station),
        datasets: [{
            label: 'Total Violations',
            data: stationStats.slice(0, 10).map(r => r.total),
            backgroundColor: 'rgba(108,99,255,0.7)',
            borderRadius: 4,
        }],
    }

    const opts = {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: { grid: { color: 'rgba(42,51,85,.5)' }, ticks: { color: '#9faac3' } },
            x: { grid: { display: false }, ticks: { color: '#9faac3', maxTicksLimit: 12 } },
        },
    }

    return (
        <div>
            <div className="kpi-grid">
                <KPI label="Total Violations" value="298,450" sub="Nov 2023 – Apr 2024" color="#ff4757" />
                <KPI label="Unique Vehicles" value="231,890" sub="Unique plates recorded" color="#6c63ff" />
                <KPI label="Repeat Offenders" value="35,587" sub="15.4% of all vehicles" color="#ffd700" />
                <KPI label="Avg Response Lag" value="468h" sub="Median 428h (18 days!)" color="#43d9ad" />
            </div>
            <div className="charts-grid-2">
                <div className="chart-card">
                    <h3 className="chart-title">Hourly Distribution</h3>
                    <p className="chart-sub">Peak at 5AM (11.4%) — 75.4% violations between 10PM–6AM</p>
                    <div style={{ height: 220 }}>{!loading && <Bar data={hourlyData} options={opts} />}</div>
                </div>
                <div className="chart-card">
                    <h3 className="chart-title">Top 10 Police Stations</h3>
                    <p className="chart-sub">Upparpet dominates with 11.5% of all citywide violations</p>
                    <div style={{ height: 220 }}>
                        {!loading && <Bar data={stationData} options={{ ...opts, indexAxis: 'y' }} />}
                    </div>
                </div>
            </div>
        </div>
    )
}

// Demo data matching actual dataset analysis
const DEMO_HOURLY = [
    { hour: 0, count: 21760 }, { hour: 1, count: 17155 }, { hour: 2, count: 24770 }, { hour: 3, count: 25707 },
    { hour: 4, count: 29102 }, { hour: 5, count: 34085 }, { hour: 6, count: 26890 }, { hour: 7, count: 14608 },
    { hour: 8, count: 8556 }, { hour: 9, count: 3145 }, { hour: 10, count: 518 }, { hour: 11, count: 577 },
    { hour: 12, count: 219 }, { hour: 13, count: 56 }, { hour: 14, count: 16 }, { hour: 15, count: 66 },
    { hour: 16, count: 416 }, { hour: 17, count: 818 }, { hour: 18, count: 1971 }, { hour: 19, count: 10713 },
    { hour: 20, count: 11834 }, { hour: 21, count: 19763 }, { hour: 22, count: 22839 }, { hour: 23, count: 22861 },
]
const DEMO_STATIONS = [
    { station: 'Upparpet', total: 34468, unique_vehicles: 26235, avg_cis: 7.2 },
    { station: 'Shivajinagar', total: 28044, unique_vehicles: 20664, avg_cis: 6.9 },
    { station: 'Malleshwaram', total: 22200, unique_vehicles: 18797, avg_cis: 6.1 },
    { station: 'HAL Old Airport', total: 20819, unique_vehicles: 14917, avg_cis: 5.8 },
    { station: 'City Market', total: 17646, unique_vehicles: 14845, avg_cis: 5.5 },
    { station: 'Vijayanagara', total: 14652, unique_vehicles: 11122, avg_cis: 5.1 },
    { station: 'Rajajinagar', total: 10998, unique_vehicles: 8144, avg_cis: 4.9 },
    { station: 'Kodigehalli', total: 10916, unique_vehicles: 8657, avg_cis: 4.7 },
    { station: 'Magadi Road', total: 8558, unique_vehicles: 7560, avg_cis: 4.2 },
    { station: 'Jeevanbheemanagar', total: 6736, unique_vehicles: 5756, avg_cis: 3.9 },
]
