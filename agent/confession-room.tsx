'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from 'lucide-react'

async function sendMessage(message: string, sessionId = crypto.randomUUID(), clearHistory = false, thinkMode = false) {
  const url = "https://42114b8d57f7e72f.ngrok.app/prod/chat";
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: 'Act as a confession room. Roast me hard in your reply. This is my confession: ' + message,
        session_id: sessionId,
        clear_history: clearHistory,
        think_mode: thinkMode
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.message;
  } catch (error) {
    throw new Error(`Error: ${error.message}`);
  }
}

export default function ConfessionRoom() {
  const [confession, setConfession] = useState('')
  const [aiResponse, setAIResponse] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [deletedChars, setDeletedChars] = useState(0)
  const [showProofLink, setShowProofLink] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)
    try {
      const response = await sendMessage(confession)
      setAIResponse(response)
    } catch (error) {
      setError(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = () => {
    setIsDeleting(true)
    setShowProofLink(true)
  }

  useEffect(() => {
    if (isDeleting && (confession || aiResponse)) {
      const timer = setTimeout(() => {
        setConfession(prev => prev.slice(0, -1))
        setAIResponse(prev => prev.slice(0, -1))
        setDeletedChars(prev => prev + 1)
      }, 25)

      return () => clearTimeout(timer)
    } else if (isDeleting && !confession && !aiResponse) {
      setIsDeleting(false)
    }
  }, [isDeleting, confession, aiResponse])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md space-y-6">
        <h1 className="text-2xl font-bold text-center text-gray-800">Confession Room</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Textarea
            value={confession}
            onChange={(e) => setConfession(e.target.value)}
            placeholder="Enter your confession here..."
            className="w-full h-32 p-2 border rounded"
            disabled={isSubmitting || isDeleting}
          />
          <Button
            type="submit"
            className="w-full"
            disabled={!confession || isSubmitting || isDeleting}
          >
            {isSubmitting ? 'Submitting...' : 'Confess'}
          </Button>
        </form>
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {aiResponse && (
          <div className="space-y-4">
            <div className="bg-blue-100 p-4 rounded-lg">
              <h2 className="font-semibold mb-2">Sxymoonsama Response:</h2>
              <p>{aiResponse}</p>
            </div>
            <Button
              onClick={handleDelete}
              variant="destructive"
              className="w-full"
              disabled={isDeleting}
            >
              Delete Confession
            </Button>
          </div>
        )}
        {(isDeleting || deletedChars > 0) && (
          <div className="bg-yellow-100 p-4 rounded-lg mt-4">
            <p className="text-yellow-800">Memory deleted: {deletedChars} bytes</p>
          </div>
        )}
        {showProofLink && (
          <div className="mt-4 text-center">
            <Button
              onClick={() => window.open('https://ra-quote-explorer.vercel.app/reports/b3ce53da6717dbe8656070ab206f8f6e79e604d8b3b0d154f848c748bd69e320', '_blank', 'noopener,noreferrer')}
              variant="outline"
              className="text-blue-600 hover:bg-blue-50"
            >
              TEE Proof-of-deletion
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}