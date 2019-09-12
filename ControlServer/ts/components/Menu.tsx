import Rodal from 'rodal';

import 'rodal/lib/rodal.css';
import { useState } from 'react';

const Menu = ({
    onClose,
    aiParams: {
        _aimYellowGoal: [aimYellowGoal, setAimYellowGoal] = useState(true)
    } = {}
}) =>
    <Rodal visible={true} onClose={onClose} width={550} height={300}>
        <h4>Menu</h4>
        <button>Play Imperial March</button>
        
        <hr />
        <h4>AI</h4>


        Current goal: {aimYellowGoal ? 'Yellow': 'Blue'}{" "}
        <button onClick={() => setAimYellowGoal(!aimYellowGoal)}>Switch</button>
    </Rodal>


export default Menu;