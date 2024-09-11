import { useState } from 'react'
import reactLogo from './assets/react.svg'

import Dropzone from './components/Dropzone';
import MessageField from './components/MessageField';


function App() {

  return (
    <div className='h-screen flex items-center justify-center'>
      <div className=''>
        <MessageField />
        <Dropzone />
      </div>
    </div>
        )
     }

export default App
