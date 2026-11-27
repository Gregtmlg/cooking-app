import { Navigate, Routes, Route } from 'react-router-dom'
import {
  RequireAdmin,
  RequireAuth,
  RequirePasswordChanged,
  RequireProfile,
} from './auth/guards.jsx'
import { ROUTES } from './routes'
import LoginPage from './pages/LoginPage.jsx'
import ChangePasswordPage from './pages/ChangePasswordPage.jsx'
import SelectProfilePage from './pages/SelectProfilePage.jsx'
import RecipeList from './pages/RecipeList.jsx'
import RecipeDetail from './pages/RecipeDetail.jsx'
import RecipeCreate from './pages/RecipeCreate.jsx'
import RecipeEdit from './pages/RecipeEdit.jsx'
import HomePage from './pages/HomePage.jsx'
import AdminPage from './pages/admin/AdminPage.jsx'
import InventoryTab from './pages/admin/InventoryTab.jsx'
import AccountsTab from './pages/admin/AccountsTab.jsx'
import ProfilesTab from './pages/admin/ProfilesTab.jsx'
import GroupsTab from './pages/admin/GroupsTab.jsx'
import Layout from './components/Layout.jsx'

function App() {
  return (
    <Routes>
      <Route path={ROUTES.login} element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path={ROUTES.changePassword} element={<ChangePasswordPage />} />
        <Route element={<RequirePasswordChanged />}>
          <Route path={ROUTES.selectProfile} element={<SelectProfilePage />} />
          <Route element={<RequireProfile />}>
            <Route path={ROUTES.home} element={<HomePage />} />
            <Route element={<Layout />}>
              <Route path={ROUTES.recipes} element={<RecipeList />} />
              <Route path={ROUTES.recipe} element={<RecipeDetail />} />
              <Route path={ROUTES.recipeNew} element={<RecipeCreate />} />
              <Route path={ROUTES.recipeEdit} element={<RecipeEdit />} />
              {/* Back-office (J6a) : une page, des onglets = des routes enfants. */}
              <Route element={<RequireAdmin />}>
                <Route path={ROUTES.admin} element={<AdminPage />}>
                  <Route index element={<Navigate to={ROUTES.adminInventory} replace />} />
                  <Route path={ROUTES.adminInventory} element={<InventoryTab />} />
                  <Route path={ROUTES.adminAccounts} element={<AccountsTab />} />
                  <Route path={ROUTES.adminProfiles} element={<ProfilesTab />} />
                  <Route path={ROUTES.adminGroups} element={<GroupsTab />} />
                </Route>
              </Route>
            </Route>
          </Route>
        </Route>
      </Route>
    </Routes>
  )
}

export default App
