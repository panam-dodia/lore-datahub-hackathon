import { Compass } from "lucide-react";
import { BrowserRouter as Router, NavLink, Route, Routes } from "react-router-dom";
import AssetDetail from "./pages/AssetDetail.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import DependencyGraph from "./pages/DependencyGraph.jsx";
import Excavate from "./pages/Excavate.jsx";
import Knowledge from "./pages/Knowledge.jsx";
import PendingReview from "./pages/PendingReview.jsx";

function NavTab({ to, children }) {
  return (
    <NavLink
      to={to}
      end={to === "/"}
      className={({ isActive }) =>
        `text-sm pb-1 border-b-2 transition-colors ${
          isActive
            ? "border-brand text-gray-50"
            : "border-transparent text-gray-400 hover:text-gray-200"
        }`
      }
    >
      {children}
    </NavLink>
  );
}

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-8">
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-brand" strokeWidth={1.75} />
            <div className="leading-tight">
              <span className="font-serif font-semibold tracking-tight text-gray-50">
                Lore
              </span>
              <p className="text-[11px] uppercase tracking-wider text-gray-400">
                Tribal Knowledge Archaeologist
              </p>
            </div>
          </div>
          <nav className="flex items-center gap-6">
            <NavTab to="/">Dependency Graph</NavTab>
            <NavTab to="/risks">Risk List</NavTab>
            <NavTab to="/pending-review">Pending Review</NavTab>
            <NavTab to="/knowledge">Knowledge</NavTab>
          </nav>
        </header>
        <main className="p-6">
          <Routes>
            <Route path="/" element={<DependencyGraph />} />
            <Route path="/risks" element={<Dashboard />} />
            <Route path="/asset/:assetUrn" element={<AssetDetail />} />
            <Route path="/excavate/:assetUrn" element={<Excavate />} />
            <Route path="/pending-review" element={<PendingReview />} />
            <Route path="/knowledge" element={<Knowledge />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
