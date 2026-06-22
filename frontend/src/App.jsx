import {Routes, Route} from 'react-router-dom'
import RecipeList from './pages/RecipeList.jsx'
import RecipeDetail from './pages/RecipeDetail.jsx'
import RecipeCreate from './pages/RecipeCreate.jsx'
import RecipeEdit from './pages/RecipeEdit.jsx'
import Layout from './components/Layout.jsx'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<RecipeList />} />
        <Route path="/recipes/:id" element={<RecipeDetail />} />
        <Route path="/recipes/new" element={<RecipeCreate />} />
        <Route path="/recipes/:id/edit" element={<RecipeEdit />} />
      </Routes>
    </Layout>
  )
}

export default App