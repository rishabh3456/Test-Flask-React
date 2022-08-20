import React, {useState,useEffect} from 'react'

function App() {
  const [data, setdata] = useState([{}]);
  useEffect(() => {
    fetch("/mindata").then(
      response => response.json()).then(
        data => setdata(data),
        console.log(data)
      );
  },[])
  return (

    <div>App</div>
  )
}

export default App