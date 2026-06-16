import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import CityOverview from './pages/CityOverview'
import LiveHotspots from './pages/LiveHotspots'
import ForecastPanel from './pages/ForecastPanel'
import RiskRankings from './pages/RiskRankings'
import PatrolIntelligence from './pages/PatrolIntelligence'
import ExplainableAI from './pages/ExplainableAI'
import Analytics from './pages/Analytics'
import './index.css'

const PAGES = {
    overview: { label: 'City Overview', icon: '📊', component: CityOverview },
    hotspots: { label: 'Live Hotspots', icon: '🔥', component: LiveHotspots },
    forecast: { label: '72h Forecast', icon: '🔮', component: ForecastPanel },
    rankings: { label: 'Risk Rankings', icon: '📈', component: RiskRankings },
    patrol: { label: 'Patrol Intel', icon: '🚔', component: PatrolIntelligence },
    xai: { label: 'Explainable AI', icon: '🧠', component: ExplainableAI },
    analytics: { label: 'Analytics', icon: '📉', component: Analytics },
}

export default function App() {
    const [activePage, setActivePage] = useState('overview')
    const PageComponent = PAGES[activePage].component

    return (
        <div className="app-shell">
            <Sidebar pages={PAGES} activePage={activePage} onNavigate={setActivePage} />
            <div className="main-content">
                <Topbar pageLabel={PAGES[activePage].label} />
                <div className="page-body">
                    <PageComponent />
                </div>
            </div>
        </div>
    )
}
