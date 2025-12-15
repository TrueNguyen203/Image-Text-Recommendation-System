import { useLocation } from 'react-router-dom';

export default function Preference() {
  const location = useLocation();
  const history = location.state?.history;
  console.log(history)
  return (
    <div>
      <h1>Preference Page</h1>
    </div>
  )

}