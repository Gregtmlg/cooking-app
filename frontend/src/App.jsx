import { Routes, Route } from 'react-router-dom'
import { RequireAuth, RequirePasswordChanged, RequireProfile } from './auth/guards.jsx'
import LoginPage from './pages/LoginPage.jsx'
import ChangePasswordPage from './pages/ChangePasswordPage.jsx'
import SelectProfilePage from './pages/SelectProfilePage.jsx'
import RecipeList from './pages/RecipeList.jsx'
import RecipeDetail from './pages/RecipeDetail.jsx'
import RecipeCreate from './pages/RecipeCreate.jsx'
import RecipeEdit from './pages/RecipeEdit.jsx'
import HomePage from './pages/HomePage.jsx'
import Layout from './components/Layout.jsx'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route element={<RequirePasswordChanged />}>
          <Route path="/select-profile" element={<SelectProfilePage />} />
          <Route element={<RequireProfile />}>
            <Route path="/" element={<HomePage />} />
            <Route element={<Layout />}>
              <Route path="/recipes" element={<RecipeList />} />
              <Route path="/recipes/:id" element={<RecipeDetail />} />
              <Route path="/recipes/new" element={<RecipeCreate />} />
              <Route path="/recipes/:id/edit" element={<RecipeEdit />} />
            </Route>
          </Route>
        </Route>
      </Route>
    </Routes>
  )
}

export default App