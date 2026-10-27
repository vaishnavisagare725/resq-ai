import { afterEach, describe, expect, it, vi } from 'vitest'
import { distanceKm, timeAgo } from './utils'

describe('distanceKm', () => {
  it('is zero for the same point', () => {
    expect(distanceKm({ lat: 18.5, lng: 73.8 }, { lat: 18.5, lng: 73.8 })).toBe(0)
  })

  it('Pune to Mumbai is about 120 km in a straight line', () => {
    const km = distanceKm({ lat: 18.5204, lng: 73.8567 }, { lat: 19.076, lng: 72.8777 })
    expect(km).toBeGreaterThan(110)
    expect(km).toBeLessThan(130)
  })

  it('is the same in both directions', () => {
    const a = { lat: 18.5, lng: 73.8 }
    const b = { lat: 28.6, lng: 77.2 }
    expect(distanceKm(a, b)).toBeCloseTo(distanceKm(b, a), 6)
  })
})

describe('timeAgo', () => {
  afterEach(() => vi.useRealTimers())

  it('formats seconds, minutes, hours and days', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-10-23T12:00:00Z'))
    expect(timeAgo('2026-10-23T11:59:50Z')).toBe('just now')
    expect(timeAgo('2026-10-23T11:55:00Z')).toBe('5 min ago')
    expect(timeAgo('2026-10-23T09:00:00Z')).toBe('3 h ago')
    expect(timeAgo('2026-10-21T12:00:00Z')).toBe('2 d ago')
  })
})