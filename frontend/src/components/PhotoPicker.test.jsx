import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import PhotoPicker from './PhotoPicker'

const image = (name, size = 1000) =>
  new File([new Uint8Array(size)], name, { type: 'image/jpeg' })

// applyAccept: false lets a test choose a file that the accept="image/*" filter would hide
const setup = () => userEvent.setup({ applyAccept: false })

describe('PhotoPicker', () => {
  it('accepts an image', async () => {
    const onChange = vi.fn()
    render(<PhotoPicker files={[]} onChange={onChange} />)
    await setup().upload(screen.getByLabelText('Add photos'), image('a.jpg'))
    expect(onChange).toHaveBeenCalledTimes(1)
    expect(onChange.mock.calls[0][0]).toHaveLength(1)
  })

  it('rejects a file that is not an image', async () => {
    const onChange = vi.fn()
    render(<PhotoPicker files={[]} onChange={onChange} />)
    const notes = new File(['hello'], 'notes.txt', { type: 'text/plain' })
    await setup().upload(screen.getByLabelText('Add photos'), notes)
    expect(onChange).not.toHaveBeenCalled()
    expect(screen.getByText(/notes\.txt is not an image/)).toBeInTheDocument()
  })

  it('rejects a photo over 5 MB', async () => {
    const onChange = vi.fn()
    render(<PhotoPicker files={[]} onChange={onChange} />)
    await setup().upload(screen.getByLabelText('Add photos'), image('big.jpg', 5 * 1024 * 1024 + 1))
    expect(onChange).not.toHaveBeenCalled()
    expect(screen.getByText(/larger than 5 MB/)).toBeInTheDocument()
  })

  it('keeps at most three photos', async () => {
    const onChange = vi.fn()
    const existing = [image('a.jpg'), image('b.jpg')]
    render(<PhotoPicker files={existing} onChange={onChange} />)
    await setup().upload(screen.getByLabelText('Add photos'), [image('c.jpg'), image('d.jpg')])
    expect(onChange.mock.calls[0][0]).toHaveLength(3)
    expect(screen.getByText(/at most 3 photos/)).toBeInTheDocument()
  })

  it('is disabled when full', () => {
    const files = [image('a.jpg'), image('b.jpg'), image('c.jpg')]
    render(<PhotoPicker files={files} onChange={vi.fn()} />)
    expect(screen.getByLabelText('Add photos')).toBeDisabled()
  })

  it('removes a photo', async () => {
    const onChange = vi.fn()
    render(<PhotoPicker files={[image('a.jpg')]} onChange={onChange} />)
    await userEvent.setup().click(screen.getByRole('button', { name: 'Remove a.jpg' }))
    expect(onChange).toHaveBeenCalledWith([])
  })
})