import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph3D from 'react-force-graph-3d'
import ForceGraph2D from 'react-force-graph-2d'
import * as THREE from 'three'
import type { GraphData, GraphNode } from '../types'

const COMPANY: Record<string, string> = {
  SCHW: '#e0c48a',
  LPLA: '#8fb596',
  RJF: '#8eb0c8',
  AMP: '#e0a48a',
  MS: '#c4a6c0',
  JPM: '#9db8a4',
  USER: '#f1d7b0',
}

function colorOf(node: GraphNode) {
  if (node.supported === false || node.type === 'user_assertion') return '#e08a45'
  return COMPANY[node.company || ''] || '#d9c4a0'
}

function place(nodes: GraphNode[]): GraphNode[] {
  const docs = nodes
    .filter((node) => node.type === 'document')
    .sort((a, b) => (a.date || '').localeCompare(b.date || '') || a.id.localeCompare(b.id))
  const index = new Map(docs.map((doc, i) => [doc.id, i]))
  const groups = new Map<string, GraphNode[]>()
  for (const node of nodes) {
    if (!node.doc_id || node.type === 'document') continue
    const list = groups.get(node.doc_id) || []
    list.push(node)
    groups.set(node.doc_id, list)
  }
  return nodes.map((node) => {
    if (node.type === 'document') {
      const i = index.get(node.id) ?? 0
      return { ...node, x: i * 280, y: 0, z: 0 }
    }
    if (node.doc_id && index.has(node.doc_id)) {
      const i = index.get(node.doc_id) ?? 0
      const k = Math.max(0, (groups.get(node.doc_id) || []).findIndex((item) => item.id === node.id))
      return { ...node, x: i * 280, y: -(110 + k * 88), z: 0 }
    }
    return { ...node, x: docs.length * 280, y: -110, z: 0 }
  })
}

function spriteLabel(text: string) {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 64
  const ctx = canvas.getContext('2d')!
  ctx.font = "600 28px 'Source Sans 3', sans-serif"
  ctx.fillStyle = '#f6efe4'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text.slice(0, 28), 256, 32)
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas), transparent: true, depthWrite: false }))
  sprite.scale.set(70, 9, 1)
  sprite.position.y = -22
  return sprite
}

function nodeObject(node: GraphNode) {
  const group = new THREE.Group()
  const radius = node.type === 'document' ? 9 : 6
  group.add(new THREE.Mesh(
    new THREE.SphereGeometry(radius, 20, 20),
    new THREE.MeshStandardMaterial({ color: new THREE.Color(colorOf(node)), roughness: 0.45, metalness: 0.12 }),
  ))
  group.add(spriteLabel(node.type === 'document' && node.detail ? `${node.label}` : node.label))
  return group
}

function dust() {
  const count = 500
  const positions = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 1800
    positions[i * 3 + 1] = (Math.random() - 0.5) * 800
    positions[i * 3 + 2] = (Math.random() - 0.5) * 1800
  }
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const mat = new THREE.PointsMaterial({ color: '#e7d3ae', size: 1.4, transparent: true, opacity: 0.7 })
  return new THREE.Points(geo, mat)
}

function pumpLayout(api: any) {
  if (!api?.pauseAnimation) return
  api.pauseAnimation()
  const orig = window.requestAnimationFrame.bind(window)
  let left = 48
  window.requestAnimationFrame = ((fn: FrameRequestCallback) => {
    if (left-- > 0) {
      fn(performance.now())
      return 1
    }
    window.requestAnimationFrame = orig
    return orig(fn)
  }) as typeof window.requestAnimationFrame
  try {
    api.d3ReheatSimulation()
    api.resumeAnimation()
  } finally {
    window.requestAnimationFrame = orig
  }
}

export function GraphView({
  data,
  mode,
  onPick,
}: {
  data: GraphData
  mode: '3d' | '2d'
  onPick: (node: GraphNode) => void
}) {
  const wrap = useRef<HTMLDivElement>(null)
  const fg = useRef<any>(null)
  const dressed = useRef(false)
  const [size, setSize] = useState({ w: 800, h: 560 })

  const fit = () => {
    const api = fg.current
    const nodes = graph.nodes
    if (!api || !nodes.length) return
    const xs = nodes.map((n) => n.x)
    const ys = nodes.map((n) => n.y)
    const zs = nodes.map((n) => n.z ?? 0)
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    const cx = (minX + maxX) / 2
    const cy = (minY + maxY) / 2
    const cz = (Math.min(...zs) + Math.max(...zs)) / 2
    const spanX = Math.max(maxX - minX, 80)
    const spanY = Math.max(maxY - minY, 80)
    if (mode === '3d') {
      const cam = api.camera()
      const fov = (cam.fov * Math.PI) / 180
      const aspect = size.w / Math.max(size.h, 1)
      const distY = spanY / 2 / Math.tan(fov / 2)
      const distX = spanX / 2 / (Math.tan(fov / 2) * aspect)
      const dist = Math.max(distX, distY) * 1.35
      api.cameraPosition({ x: cx, y: cy, z: cz + dist }, { x: cx, y: cy, z: cz }, 0)
    } else {
      const zoom = Math.min((size.w - 48) / (spanX + 220), (size.h - 48) / (spanY + 80))
      api.centerAt(cx, cy, 0)
      api.zoom(Math.max(zoom, 0.2), 0)
    }
  }

  useEffect(() => {
    const measure = () => {
      const rect = wrap.current?.getBoundingClientRect()
      if (!rect) return
      const next = { w: Math.max(320, rect.width), h: Math.max(320, rect.height) }
      setSize((prev) => (Math.abs(prev.w - next.w) < 24 && Math.abs(prev.h - next.h) < 24 ? prev : next))
    }
    measure()
    const obs = new ResizeObserver(measure)
    if (wrap.current) obs.observe(wrap.current)
    return () => obs.disconnect()
  }, [])

  const graph = useMemo(
    () => ({
      nodes: place(data.nodes).map((n) => ({ ...n, fx: n.x, fy: n.y, fz: n.z })),
      links: data.links.map((l) => ({ ...l })),
    }),
    [data, mode],
  )

  const laidOut = data.nodes.map((n) => `${n.id}:${n.x}:${n.y}`).join('|')
  useEffect(() => {
    const run = (pump: boolean) => {
      const api = fg.current
      if (!api) return
      if (pump && mode === '3d') pumpLayout(api)
      fit()
    }
    const first = window.setTimeout(() => run(true), 200)
    const again = window.setTimeout(() => run(false), 700)
    return () => {
      window.clearTimeout(first)
      window.clearTimeout(again)
    }
  }, [laidOut, mode, size.w, size.h])

  useEffect(() => {
    dressed.current = false
  }, [mode])

  useEffect(() => {
    if (mode !== '3d' || !fg.current || dressed.current) return
    dressed.current = true
    const scene: THREE.Scene = fg.current.scene()
    scene.add(new THREE.AmbientLight(0xfff1dd, 1.4))
    const key = new THREE.DirectionalLight(0xffe2b8, 1.6)
    key.position.set(40, 80, 60)
    scene.add(key)
    const stars = dust()
    ;(stars as unknown as { __graphObjType: string }).__graphObjType = 'decor'
    scene.add(stars)
  }, [mode, data])

  const linkColor = (link: any) => (link.type === 'contradicts' ? '#e08a45' : 'rgba(232, 214, 186, 0.45)')

  return (
    <div ref={wrap} className="stage absolute inset-0">
      {mode === '3d' ? (
        <ForceGraph3D
          ref={fg}
          width={size.w}
          height={size.h}
          graphData={graph}
          backgroundColor="#16110e"
          nodeThreeObject={(node: any) => nodeObject(node)}
          nodeLabel={(node: any) => node.title || node.label}
          linkColor={linkColor}
          linkWidth={(link: any) => (link.type === 'contradicts' ? 1.4 : 0.4)}
          linkOpacity={0.85}
          onNodeClick={(node: any) => onPick(node)}
          showNavInfo={false}
          enableNodeDrag={false}
          cooldownTicks={0}
        />
      ) : (
        <ForceGraph2D
          ref={fg}
          width={size.w}
          height={size.h}
          graphData={graph}
          backgroundColor="#1c1612"
          cooldownTicks={0}
          nodeRelSize={4}
          nodeColor={() => 'rgba(0,0,0,0)'}
          linkColor={linkColor}
          linkWidth={(link: any) => (link.type === 'contradicts' ? 1.6 : 0.6)}
          linkLineDash={(link: any) => (link.type === 'contradicts' ? [4, 3] : null)}
          onNodeClick={(node: any) => onPick(node)}
          nodeCanvasObjectMode={() => 'after'}
          nodeCanvasObject={(node: any, ctx, scale) => {
            const r = node.type === 'document' || node.type === 'company' ? 6.5 : 4.2
            ctx.beginPath()
            ctx.arc(node.x, node.y, r, 0, Math.PI * 2)
            ctx.fillStyle = colorOf(node)
            ctx.fill()
            ctx.lineWidth = 1.1 / scale
            ctx.strokeStyle = node.supported === false ? '#e08a45' : '#f6efe4'
            ctx.setLineDash(node.tier === 'secondary' || node.supported === false ? [3 / scale, 2 / scale] : [])
            ctx.stroke()
            ctx.setLineDash([])
            const lines = [node.label, node.type === 'document' ? node.detail : '']
              .filter(Boolean)
              .map((line: string) => String(line).slice(0, 22))
            ctx.save()
            ctx.translate(node.x, node.y)
            ctx.scale(1 / scale, 1 / scale)
            ctx.textAlign = 'center'
            ctx.textBaseline = 'top'
            lines.forEach((line: string, index: number) => {
              ctx.font = index === 0 ? '600 11px "Source Sans 3", sans-serif' : '500 10px "Source Sans 3", sans-serif'
              ctx.fillStyle = index === 0 ? '#f6efe4' : '#e7d3ae'
              ctx.fillText(line, 0, r * scale + 5 + index * 13)
            })
            ctx.restore()
          }}
          nodePointerAreaPaint={(node: any, color, ctx) => {
            ctx.fillStyle = color
            ctx.beginPath()
            ctx.arc(node.x, node.y, 10, 0, Math.PI * 2)
            ctx.fill()
          }}
        />
      )}
      <div className="pointer-events-none absolute bottom-3 left-4 right-4 flex justify-between text-[11px] tracking-wide text-[#e7d7c2]/80">
        <span>Evidence plane · older to newer</span>
        <span>{mode === '3d' ? 'Drag to rotate · scroll to zoom' : 'Scroll to zoom · drag to pan'}</span>
      </div>
    </div>
  )
}
