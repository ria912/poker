import React, { useState, useMemo } from 'react';
import axios from 'axios';

// APIのベースURL（FastAPIサーバーのアドレス）
const API_URL = 'http://127.0.0.1:8000';

// カードのスートを絵文字に変換するヘルパー
const suitToEmoji = {
  'H': '♥', // Hearts
  'D': '♦', // Diamonds
  'C': '♣', // Clubs
  'S': '♠', // Spades
};

// カードコンポーネント
const Card = ({ rank, suit }) => {
  const color = (suit === 'H' || suit === 'D') ? 'text-red-500' : 'text-black';
  return (
    <div className={`w-16 h-24 bg-white border border-gray-300 rounded-lg flex flex-col justify-center items-center shadow-md ${color}`}>
      <span className="text-3xl font-bold">{rank}</span>
      <span className="text-2xl">{suitToEmoji[suit]}</span>
    </div>
  );
};

function App() {
  const [playerName, setPlayerName] = useState('Hero');
  const [gameState, setGameState] = useState(null);
  const [gameId, setGameId] = useState(null);
  const [humanPlayerId, setHumanPlayerId] = useState(null);
  const [raiseAmount, setRaiseAmount] = useState(0);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // --- API通信関数 ---

  const createGame = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/games`, {
        players: [
          { name: playerName, stack: 1000, is_ai: false },
          { name: 'AI Bot 1', stack: 1000, is_ai: true },
          { name: 'AI Bot 2', stack: 1000, is_ai: true },
        ],
        small_blind: 10,
        big_blind: 20,
      });
      const data = response.data;
      setGameState(data);
      setGameId(data.game_id);
      // レスポンスから人間プレイヤーのIDを見つけて保存
      const human = data.seats.find(s => s.player && !s.player.is_ai);
      if (human) {
        setHumanPlayerId(human.player.player_id);
      }
    } catch (err) {
      setError('Failed to create game. Is the server running?');
      console.error(err);
    }
    setIsLoading(false);
  };

  const sendAction = async (actionType, amount = null) => {
    if (!gameId || !humanPlayerId) return;
    setIsLoading(true);
    setError('');
    try {
      const payload = {
        player_id: humanPlayerId,
        action_type: actionType,
        amount: amount,
      };
      const response = await axios.post(`${API_URL}/games/${gameId}/action`, payload);
      setGameState(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred.');
      console.error(err);
    }
    setIsLoading(false);
  };
  
  const startNextHand = async () => {
    if (!gameId) return;
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/games/${gameId}/next_hand`);
      setGameState(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start next hand.');
      console.error(err);
    }
    setIsLoading(false);
  };


  // --- ヘルパーとメモ化 ---

  const humanPlayerSeat = useMemo(() => {
    if (!gameState) return null;
    return gameState.seats.find(s => s.player?.player_id === humanPlayerId);
  }, [gameState, humanPlayerId]);

  const isMyTurn = useMemo(() => {
    if (!gameState || !humanPlayerSeat) return false;
    return gameState.current_seat_index === humanPlayerSeat.index && gameState.status === 'IN_PROGRESS';
  }, [gameState, humanPlayerSeat]);

  const validActions = useMemo(() => {
     if (!isMyTurn || !gameState.valid_actions) return {};
     const actions = {};
     gameState.valid_actions.forEach(action => {
         actions[action.type] = action;
     });
     return actions;
  }, [isMyTurn, gameState]);


  // --- レンダリング ---
  
  if (!gameState) {
    return (
      <div className="min-h-screen bg-gray-100 flex flex-col justify-center items-center p-4">
        <div className="w-full max-w-sm p-8 bg-white rounded-xl shadow-lg text-center">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">Texas Hold'em</h1>
            <p className="text-gray-600 mb-6">Enter your name to start a new game.</p>
            <input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your Name"
            />
            <button
                onClick={createGame}
                disabled={isLoading || !playerName}
                className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-gray-400"
            >
                {isLoading ? 'Creating...' : 'Create Game'}
            </button>
            {error && <p className="text-red-500 mt-4">{error}</p>}
        </div>
      </div>
    );
  }

  // ゲームテーブル画面
  return (
    <div className="min-h-screen bg-green-800 text-white p-4 flex flex-col items-center font-sans">
      <div className="w-full max-w-6xl">

        {/* 上部情報 */}
        <div className="text-center mb-4">
            <h1 className="text-2xl">Game ID: {gameId.substring(0,8)}...</h1>
            {gameState.last_message && <p className="text-yellow-300 bg-black bg-opacity-20 p-2 rounded-lg mt-2">{gameState.last_message}</p>}
        </div>

        {/* コミュニティカードとポット */}
        <div className="flex flex-col items-center mb-6">
            <h2 className="text-xl font-bold mb-2">Community Cards</h2>
            <div className="flex space-x-2 mb-2">
            {gameState.community_cards.length > 0 ? gameState.community_cards.map((card, i) => (
                <Card key={i} rank={card.rank} suit={card.suit} />
            )) : <div className="h-24 w-16 text-gray-400 flex items-center justify-center">(No cards yet)</div> }
            </div>
            <p className="text-2xl font-bold bg-black bg-opacity-40 px-4 py-1 rounded-full">Pot: ${gameState.pot}</p>
        </div>

        {/* プレイヤーたち */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {gameState.seats.map(seat => (
            seat.is_occupied ? (
            <div key={seat.index} className={`p-4 rounded-lg shadow-xl relative ${isMyTurn && gameState.current_seat_index === seat.index ? 'bg-yellow-500 border-4 border-yellow-300' : 'bg-green-700 border-2 border-green-600'}`}>
                <div className="font-bold text-lg">{seat.player.name} {seat.position ? `(${seat.position})` : ''}</div>
                <div className="text-yellow-300 text-xl">${seat.stack}</div>
                <div>Status: {seat.status}</div>
                {seat.current_bet > 0 && <div className="absolute -top-3 -right-3 bg-red-600 rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm border-2 border-white">{seat.current_bet}</div>}

                {/* 手札表示 */}
                <div className="flex space-x-2 mt-2 h-24">
                  {seat.player.player_id === humanPlayerId && seat.hole_cards.length > 0 ? (
                    seat.hole_cards.map((card, i) => <Card key={i} rank={card.rank} suit={card.suit} />)
                  ) : (
                    <div className="text-gray-400 flex items-center justify-center w-full">{seat.status === 'FOLDED' ? 'FOLDED' : ' '}</div>
                  )}
                </div>
            </div>
            ) : <div key={seat.index} className="p-4 rounded-lg bg-black bg-opacity-20 text-center text-gray-400">Empty Seat</div>
          ))}
        </div>

        {/* アクションパネル */}
        {error && <p className="text-red-400 bg-red-900 p-2 rounded-lg text-center mb-4">{error}</p>}
        
        {isMyTurn && (
          <div className="bg-black bg-opacity-50 p-4 rounded-lg flex items-center justify-center space-x-2">
            {validActions.FOLD && <button onClick={() => sendAction('FOLD')} className="action-button bg-gray-500 hover:bg-gray-600">Fold</button>}
            {validActions.CHECK && <button onClick={() => sendAction('CHECK')} className="action-button bg-blue-500 hover:bg-blue-600">Check</button>}
            {validActions.CALL && <button onClick={() => sendAction('CALL', validActions.CALL.amount)} className="action-button bg-green-500 hover:bg-green-600">Call ${validActions.CALL.amount}</button>}
            
            {validActions.RAISE && (
              <div className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 p-2 rounded-lg">
                <input 
                  type="range"
                  min={validActions.RAISE.min}
                  max={validActions.RAISE.max}
                  step="10"
                  value={raiseAmount}
                  onChange={e => setRaiseAmount(Number(e.target.value))}
                  className="w-48"
                />
                <input 
                  type="number"
                  value={raiseAmount}
                  onChange={e => setRaiseAmount(Number(e.target.value))}
                  className="w-24 p-2 rounded text-black"
                />
                <button onClick={() => sendAction('RAISE', raiseAmount)} className="action-button bg-transparent text-white font-bold">Raise</button>
              </div>
            )}
            {validActions.BET && (
               <div className="flex items-center space-x-2 bg-purple-500 hover:bg-purple-600 p-2 rounded-lg">
                <input type="number" onChange={e => setRaiseAmount(Number(e.target.value))} className="w-24 p-2 rounded text-black" placeholder={`Min ${validActions.BET.min}`}/>
                <button onClick={() => sendAction('BET', raiseAmount)} className="action-button bg-transparent text-white font-bold">Bet</button>
              </div>
            )}
          </div>
        )}

        {gameState.status === 'HAND_COMPLETE' && (
           <div className="text-center mt-4">
             <button onClick={startNextHand} className="action-button bg-indigo-600 hover:bg-indigo-700">Start Next Hand</button>
           </div>
        )}

      </div>
    </div>
  );
}

export default App;
