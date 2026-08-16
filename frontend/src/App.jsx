import { Routes, Route } from 'react-router-dom'
import RecipeList from './pages/RecipeList.jsx'
import RecipeDetail from './pages/RecipeDetail.jsx'
import RecipeCreate from './pages/RecipeCreate.jsx'
import RecipeEdit from './pages/RecipeEdit.jsx'
import HomePage from './pages/HomePage.jsx'
import Layout from './components/Layout.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route element={<Layout />}>
        <Route path="/recipes" element={<RecipeList />} />
        <Route path="/recipes/:id" element={<RecipeDetail />} />
        <Route path="/recipes/new" element={<RecipeCreate />} />
        <Route path="/recipes/:id/edit" element={<RecipeEdit />} />
      </Route>
    </Routes>
  )
}

export default App