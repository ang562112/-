import { Toaster } from 'react-hot-toast';
import FallingStarlight from './components/FallingStarlight';
import ProfileCard from './components/ProfileCard';

function App() {
  return (
    <div className="relative min-h-screen w-full flex items-center justify-center p-4 selection:bg-aptos/30 selection:text-aptos text-white">
      <FallingStarlight />
      <div className="relative w-full flex justify-center z-10">
        <ProfileCard />
      </div>
      <Toaster
        position="bottom-center"
        toastOptions={{
          style: {
            background: '#18181B',
            color: '#fff',
            border: '1px solid rgba(45, 216, 167, 0.2)'
          }
        }}
      />
    </div>
  )
}

export default App
