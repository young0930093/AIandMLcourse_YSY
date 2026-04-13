import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

function renderText(text) {
  if (!text) return null
  return text.split('\n').map((line, i) => {
    const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/)
    return (
      <span key={i}>
        {parts.map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>
          }
          if (part.startsWith('`') && part.endsWith('`')) {
            return <code key={j} className="bg-pink-50 text-pink-700 px-1 py-0.5 rounded text-sm font-mono">{part.slice(1, -1)}</code>
          }
          return part
        })}
        {i < text.split('\n').length - 1 && <br />}
      </span>
    )
  })
}

function renderBody(body) {
  if (!body) return null
  const lines = body.split('\n')
  const elements = []
  let tableLines = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.startsWith('|')) {
      tableLines.push(line)
    } else {
      if (tableLines.length > 0) {
        elements.push(<TableRenderer key={i} lines={tableLines} />)
        tableLines = []
      }
      if (line.startsWith('- ')) {
        elements.push(
          <li key={i} className="text-gray-600 text-sm leading-relaxed ml-4 list-disc">
            {renderText(line.slice(2))}
          </li>
        )
      } else if (line.trim()) {
        elements.push(
          <p key={i} className="text-gray-600 text-sm leading-relaxed">
            {renderText(line)}
          </p>
        )
      } else {
        elements.push(<div key={i} className="h-2" />)
      }
    }
  }
  if (tableLines.length > 0) {
    elements.push(<TableRenderer key="table-end" lines={tableLines} />)
  }
  return elements
}

function TableRenderer({ lines }) {
  const rows = lines.filter(l => !l.match(/^\|[-| :]+\|$/))
  const headers = rows[0]?.split('|').filter(Boolean).map(h => h.trim())
  const body = rows.slice(1)
  return (
    <div className="overflow-x-auto my-3">
      <table className="min-w-full text-sm border-collapse">
        <thead>
          <tr className="bg-pink-50">
            {headers?.map((h, i) => (
              <th key={i} className="border border-pink-200 px-3 py-2 text-left text-pink-700 font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-pink-50/30'}>
              {row.split('|').filter(Boolean).map((cell, j) => (
                <td key={j} className="border border-pink-100 px-3 py-2 text-gray-600">{renderText(cell.trim())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function LectureContent({ content }) {
  if (!content) return null
  const { sections } = content

  return (
    <div className="space-y-8">
      {sections.map((section, idx) => (
        <div key={idx} className="bg-white rounded-2xl border border-pink-100 p-6 shadow-sm">
          <h3 className="font-bold text-gray-800 text-lg mb-4 flex items-center gap-2">
            <span className="w-7 h-7 bg-gradient-to-br from-pink-300 to-pink-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
              {idx + 1}
            </span>
            {section.title}
          </h3>
          {section.body && (
            <div className="mb-4 space-y-1">{renderBody(section.body)}</div>
          )}
          {section.code && (
            <div className="rounded-xl overflow-hidden border border-pink-100">
              <div className="bg-pink-50 px-4 py-2 flex items-center gap-2 border-b border-pink-100">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <span className="text-xs text-pink-400 font-medium">Python</span>
              </div>
              <SyntaxHighlighter
                language="python"
                style={oneLight}
                customStyle={{ margin: 0, borderRadius: 0, fontSize: '0.8rem', background: '#fff' }}
              >
                {section.code}
              </SyntaxHighlighter>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
