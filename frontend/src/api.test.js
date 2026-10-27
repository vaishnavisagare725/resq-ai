import { describe, expect, it } from 'vitest'
import { errorMessages } from './api'

describe('errorMessages', () => {
  it('explains an unreachable server', () => {
    expect(errorMessages({})).toEqual(['Cannot reach the server. Is Django running?'])
  })

  it('lists every field error', () => {
    const err = { response: { data: { password: ['too short', 'too common'], username: 'taken' } } }
    expect(errorMessages(err)).toEqual([
      'password: too short',
      'password: too common',
      'username: taken',
    ])
  })

  it('uses the detail message', () => {
    expect(errorMessages({ response: { data: { detail: 'Not found.' } } })).toEqual(['Not found.'])
  })

  it('does not show an HTML error page to the user', () => {
    expect(errorMessages({ response: { data: '<html>500</html>' } })).toEqual([
      'Something went wrong on the server.',
    ])
  })
})